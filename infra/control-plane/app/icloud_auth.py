"""iCloud Drive authentication and file browsing via pyicloud.

Uses pyicloud to authenticate with Apple (including 2FA) and browse
iCloud Drive contents. Sessions persist via pyicloud's cookie jar
(~2 months before re-auth needed).
"""

from __future__ import annotations

import logging
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger("control-plane.icloud")

router = APIRouter(prefix="/api/icloud", tags=["icloud"])

COOKIE_DIR = Path("/home/claude-operator/.pyicloud")

# ---------------------------------------------------------------------------
# Global pyicloud session
# ---------------------------------------------------------------------------

_api = None  # PyiCloudService instance
_state: str = "idle"  # idle | awaiting_2fa | authenticated | error


def _get_api():
    """Return the current pyicloud API instance or None."""
    global _api, _state
    if _api is None:
        return None
    # Check if session is still valid by testing a lightweight call
    try:
        _api.is_trusted_session
        return _api
    except Exception:
        _api = None
        _state = "idle"
        return None


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SignInRequest(BaseModel):
    apple_id: str
    password: str


class VerifyRequest(BaseModel):
    code: str


# ---------------------------------------------------------------------------
# Helper: walk iCloud Drive path
# ---------------------------------------------------------------------------

def _resolve_drive_path(path: str):
    """Navigate to a path in iCloud Drive, return the node.

    Path is slash-separated, e.g. '' (root), 'Documents', 'Documents/Notes'.
    """
    if _api is None:
        raise HTTPException(401, detail="Not authenticated with iCloud")

    node = _api.drive
    if not path or path == "/":
        return node

    parts = [p for p in path.strip("/").split("/") if p]
    for part in parts:
        try:
            node = node[part]
        except (KeyError, IndexError):
            raise HTTPException(404, detail=f"Path not found: {path}")
    return node


def _node_to_dict(node) -> dict[str, Any]:
    """Convert a pyicloud drive node to a JSON-serializable dict."""
    data = node.data or {}
    is_dir = node.type in ("folder", "app_library")
    name = node.name or data.get("drivewsid", "unknown")
    result = {
        "name": name,
        "type": "dir" if is_dir else "file",
    }
    if not is_dir:
        result["size"] = data.get("size", 0)
        result["modified"] = data.get("dateModified", "")
        result["extension"] = data.get("extension", "")
    return result


# ---------------------------------------------------------------------------
# Routes: Auth
# ---------------------------------------------------------------------------

@router.get("/status")
async def icloud_status() -> dict:
    """Check if we have a valid iCloud session."""
    api = _get_api()
    return {
        "authenticated": api is not None,
        "auth_state": _state,
        "trusted": api.is_trusted_session if api else False,
    }


@router.post("/auth/start")
async def start_auth(req: SignInRequest) -> dict:
    """Sign in with Apple ID + password. Triggers 2FA push."""
    global _api, _state

    try:
        from pyicloud import PyiCloudService

        COOKIE_DIR.mkdir(parents=True, exist_ok=True)
        _api = PyiCloudService(
            req.apple_id,
            req.password,
            cookie_directory=str(COOKIE_DIR),
        )
    except Exception as exc:
        _api = None
        _state = "error"
        logger.exception("iCloud sign-in failed")
        raise HTTPException(401, detail=f"Sign-in failed: {exc}")

    if _api.requires_2fa:
        _state = "awaiting_2fa"
        return {
            "status": "2fa_required",
            "message": "Enter the verification code from your Apple device",
        }
    elif _api.requires_2sa:
        _state = "awaiting_2fa"
        return {
            "status": "2fa_required",
            "message": "Enter the verification code (2SA)",
        }
    else:
        # No 2FA needed — already trusted session
        _state = "authenticated"
        return {"status": "authenticated"}


@router.post("/auth/verify")
async def verify_2fa(req: VerifyRequest) -> dict:
    """Submit the 2FA/2SA code."""
    global _state

    if _api is None or _state != "awaiting_2fa":
        raise HTTPException(400, detail="No active auth session awaiting 2FA")

    try:
        if _api.requires_2fa:
            ok = _api.validate_2fa_code(req.code)
            if not ok:
                raise HTTPException(401, detail="Invalid verification code")
            # Trust the session so we don't get challenged again
            if not _api.is_trusted_session:
                _api.trust_session()
        elif _api.requires_2sa:
            devices = _api.trusted_devices
            # Use first device for 2SA
            device = devices[0] if devices else None
            if device:
                _api.validate_verification_code(device, req.code)
            else:
                raise HTTPException(400, detail="No trusted devices found for 2SA")
    except HTTPException:
        raise
    except Exception as exc:
        _state = "error"
        logger.exception("2FA verification failed")
        raise HTTPException(401, detail=f"Verification failed: {exc}")

    _state = "authenticated"
    return {"status": "authenticated"}


@router.post("/auth/logout")
async def logout() -> dict:
    """Clear the iCloud session."""
    global _api, _state
    _api = None
    _state = "idle"
    return {"status": "logged_out"}


# ---------------------------------------------------------------------------
# Routes: Drive browsing
# ---------------------------------------------------------------------------

@router.get("/drive/list")
async def drive_list(path: str = Query("", description="Slash-separated path")) -> dict:
    """List contents of an iCloud Drive directory."""
    if _api is None or _state != "authenticated":
        raise HTTPException(401, detail="Not authenticated with iCloud")

    try:
        node = _resolve_drive_path(path)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, detail=f"Failed to resolve path: {exc}")

    try:
        children = node.dir()
    except Exception:
        children = []

    entries = []
    for name in children:
        try:
            child = node[name]
            entries.append(_node_to_dict(child))
        except Exception:
            entries.append({"name": name, "type": "file", "size": 0})

    # Sort: dirs first, then alphabetical
    entries.sort(key=lambda e: (0 if e["type"] == "dir" else 1, e["name"].lower()))

    return {
        "path": path or "/",
        "entries": entries[:500],
    }


@router.get("/drive/download")
async def drive_download(path: str = Query(..., description="Slash-separated path to file")):
    """Download a file from iCloud Drive."""
    if _api is None or _state != "authenticated":
        raise HTTPException(401, detail="Not authenticated with iCloud")

    node = _resolve_drive_path(path)

    if node.type in ("folder", "app_library"):
        raise HTTPException(400, detail="Cannot download a folder")

    try:
        response = node.open(stream=True)
        content_type = mimetypes.guess_type(node.name or "file")[0] or "application/octet-stream"
        filename = node.name or "download"

        return StreamingResponse(
            response.iter_content(chunk_size=65536),
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.exception("iCloud download failed")
        raise HTTPException(500, detail=f"Download failed: {exc}")
