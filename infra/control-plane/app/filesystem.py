"""File browser backend for the ML Lab control plane.

Provides local filesystem and S3 browsing, upload, download, and management
APIs. All local paths are sandboxed against an allowlist with symlink-aware
traversal prevention.
"""

from __future__ import annotations

import logging
import mimetypes
import os
import stat
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse

logger = logging.getLogger("control-plane.fs")

router = APIRouter(prefix="/api/fs")

# Set by main.py at startup — holds the shared ElevationManager instance.
_elevation: Any = None


def set_elevation_manager(em: Any) -> None:
    """Store a reference to the shared ElevationManager instance.

    Args:
        em: The ElevationManager instance from main.py.
    """
    global _elevation
    _elevation = em

MAX_ENTRIES = 500

# ---------------------------------------------------------------------------
# Path sandboxing
# ---------------------------------------------------------------------------

# Each entry maps a resolved directory prefix to whether writes are allowed.
_ALLOWED_PATHS: list[tuple[str, bool]] = [
    ("/home/claude-operator/projects", True),
    ("/home/claude-operator/lab", True),
    ("/home/claude-operator/icloud", True),
    ("/opt/control-plane", False),
]


def _check_path(path: str, *, require_writable: bool = False) -> str:
    """Resolve *path* and verify it falls within the allowlist.

    Args:
        path: The raw path supplied by the caller.
        require_writable: If ``True``, the resolved path must be inside a
            read-write allowlisted directory.

    Returns:
        The resolved (real) absolute path.

    Raises:
        HTTPException: 403 if the path is outside the allowlist or a write
            is attempted against a read-only root.
        HTTPException: 404 if the resolved path does not exist (only when
            *require_writable* is ``False``).
    """
    resolved = os.path.realpath(path)

    for allowed_root, writable in _ALLOWED_PATHS:
        # Ensure we match on a directory boundary by appending os.sep.
        if resolved == allowed_root or resolved.startswith(allowed_root + os.sep):
            if require_writable and not writable:
                raise HTTPException(
                    status_code=403,
                    detail=f"Write operations are not permitted under {allowed_root}",
                )
            return resolved

    raise HTTPException(status_code=403, detail="Path is outside the allowed directories")


# ---------------------------------------------------------------------------
# Local filesystem endpoints
# ---------------------------------------------------------------------------


@router.get("/local/list")
async def local_list(
    path: str = Query("/home/claude-operator/projects"),
) -> dict[str, Any]:
    """List directory contents.

    Args:
        path: Absolute path to the directory to list.

    Returns:
        Dict with *path*, *parent*, *entries* (list of dicts with *name*,
        *type*, *size*, *modified*), and *writable* flag.
    """
    resolved = _check_path(path)

    if not os.path.isdir(resolved):
        raise HTTPException(status_code=404, detail="Directory not found")

    # Determine writability of this root.
    writable = False
    for allowed_root, w in _ALLOWED_PATHS:
        if resolved == allowed_root or resolved.startswith(allowed_root + os.sep):
            writable = w
            break

    try:
        raw_entries = os.listdir(resolved)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    dirs: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []

    for name in raw_entries:
        if len(dirs) + len(files) >= MAX_ENTRIES:
            break

        full = os.path.join(resolved, name)
        try:
            st = os.stat(full)
        except (OSError, ValueError):
            continue

        modified = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()

        if stat.S_ISDIR(st.st_mode):
            dirs.append(
                {"name": name, "type": "dir", "size": 0, "modified": modified}
            )
        else:
            files.append(
                {"name": name, "type": "file", "size": st.st_size, "modified": modified}
            )

    dirs.sort(key=lambda e: e["name"].lower())
    files.sort(key=lambda e: e["name"].lower())

    parent = os.path.dirname(resolved) if resolved != "/" else None
    # Only expose parent if it is itself within the allowlist.
    if parent is not None:
        try:
            _check_path(parent)
        except HTTPException:
            parent = None

    return {
        "path": resolved,
        "parent": parent,
        "entries": dirs + files,
        "writable": writable,
    }


@router.get("/local/download")
async def local_download(path: str = Query(...)) -> FileResponse:
    """Download a single file.

    Args:
        path: Absolute path to the file.

    Returns:
        The file content with an appropriate ``Content-Type`` header.
    """
    resolved = _check_path(path)

    if not os.path.exists(resolved):
        raise HTTPException(status_code=404, detail="File not found")
    if os.path.isdir(resolved):
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")

    content_type, _ = mimetypes.guess_type(resolved)
    if content_type is None:
        content_type = "application/octet-stream"

    filename = os.path.basename(resolved)
    return FileResponse(resolved, media_type=content_type, filename=filename)


@router.post("/local/upload")
async def local_upload(
    path: str = Query(...),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Upload a file into the given directory.

    Args:
        path: Absolute path to the target *directory*.
        file: The uploaded file.

    Returns:
        Dict with *success*, *path*, *name*, and *size*.
    """
    resolved = _check_path(path, require_writable=True)

    if not os.path.isdir(resolved):
        raise HTTPException(status_code=404, detail="Target directory not found")

    filename = file.filename or "upload"
    dest = os.path.join(resolved, filename)

    # Ensure the final destination is still inside the allowlist (guards
    # against filenames containing path separators).
    _check_path(dest, require_writable=True)

    try:
        contents = await file.read()
        with open(dest, "wb") as f:
            f.write(contents)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except OSError as exc:
        logger.exception("Failed to write uploaded file to %s", dest)
        raise HTTPException(status_code=500, detail=str(exc))

    size = os.path.getsize(dest)
    logger.info("Uploaded %s (%d bytes) to %s", filename, size, resolved)
    return {"success": True, "path": dest, "name": filename, "size": size}


@router.post("/local/mkdir")
async def local_mkdir(path: str = Query(...)) -> dict[str, Any]:
    """Create a directory.

    Args:
        path: Absolute path of the directory to create.

    Returns:
        Dict with *success* and *path*.
    """
    resolved_parent = os.path.realpath(os.path.dirname(path))
    # Validate that the parent directory is writable and allowed.
    _check_path(resolved_parent, require_writable=True)

    target = os.path.join(resolved_parent, os.path.basename(path))
    # Re-validate the full target path.
    _check_path(target, require_writable=True)

    if os.path.exists(target):
        raise HTTPException(status_code=409, detail="Path already exists")

    try:
        os.makedirs(target, exist_ok=False)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except OSError as exc:
        logger.exception("Failed to create directory %s", target)
        raise HTTPException(status_code=500, detail=str(exc))

    logger.info("Created directory %s", target)
    return {"success": True, "path": target}


@router.delete("/local/delete")
async def local_delete(path: str = Query(...)) -> dict[str, Any]:
    """Delete a file or empty directory.

    Args:
        path: Absolute path to the file or empty directory to remove.

    Returns:
        Dict with *success* and *path*.
    """
    resolved = _check_path(path, require_writable=True)

    if not os.path.exists(resolved):
        raise HTTPException(status_code=404, detail="Path not found")

    try:
        if os.path.isdir(resolved):
            os.rmdir(resolved)  # Only removes empty directories.
        else:
            os.remove(resolved)
    except OSError as exc:
        # Covers PermissionError, non-empty dir, etc.
        logger.warning("Delete failed for %s: %s", resolved, exc)
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info("Deleted %s", resolved)
    return {"success": True, "path": resolved}


# ---------------------------------------------------------------------------
# S3 endpoints
# ---------------------------------------------------------------------------

_s3_client = boto3.client("s3")

_PRESIGN_THRESHOLD = 10 * 1024 * 1024  # 10 MB
_PRESIGN_EXPIRY = 3600  # 1 hour


@router.get("/s3/list")
async def s3_list(
    bucket: str = Query(...),
    prefix: str = Query(""),
) -> dict[str, Any]:
    """List S3 objects using folder-style (delimiter) listing.

    Args:
        bucket: S3 bucket name.
        prefix: Key prefix to list under.

    Returns:
        Dict with *bucket*, *prefix*, and *entries* (list of dicts with
        *name*, *type*, *size*, *modified*).
    """
    try:
        response = _s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter="/",
            MaxKeys=MAX_ENTRIES,
        )
    except ClientError as exc:
        logger.exception("S3 list failed for s3://%s/%s", bucket, prefix)
        raise HTTPException(status_code=502, detail=str(exc))

    entries: list[dict[str, Any]] = []

    # "Folders" from CommonPrefixes.
    for cp in response.get("CommonPrefixes", []):
        folder_prefix = cp["Prefix"]
        # Display name: strip the parent prefix and trailing slash.
        name = folder_prefix[len(prefix) :].rstrip("/")
        entries.append({"name": name, "type": "dir", "size": 0, "modified": None})

    # Files from Contents — skip the prefix itself if it appears.
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key == prefix:
            continue
        name = key[len(prefix) :]
        modified = obj["LastModified"].isoformat() if obj.get("LastModified") else None
        entries.append(
            {
                "name": name,
                "type": "file",
                "size": obj.get("Size", 0),
                "modified": modified,
            }
        )

    return {"bucket": bucket, "prefix": prefix, "entries": entries}


@router.get("/s3/download", response_model=None)
async def s3_download(
    bucket: str = Query(...),
    key: str = Query(...),
) -> RedirectResponse | StreamingResponse:
    """Download an S3 object.

    For files larger than 10 MB a presigned URL redirect is returned.
    Smaller files are streamed directly.

    Args:
        bucket: S3 bucket name.
        key: Object key.

    Returns:
        A ``StreamingResponse`` for small files or a ``RedirectResponse``
        to a presigned URL for large files.
    """
    try:
        head = _s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchKey"):
            raise HTTPException(status_code=404, detail="S3 object not found")
        logger.exception("S3 head_object failed for s3://%s/%s", bucket, key)
        raise HTTPException(status_code=502, detail=str(exc))

    size = head.get("ContentLength", 0)

    if size > _PRESIGN_THRESHOLD:
        url = _s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=_PRESIGN_EXPIRY,
        )
        return RedirectResponse(url=url)

    # Stream small files directly.
    try:
        obj = _s3_client.get_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        logger.exception("S3 get_object failed for s3://%s/%s", bucket, key)
        raise HTTPException(status_code=502, detail=str(exc))

    content_type = head.get("ContentType", "application/octet-stream")
    filename = key.rsplit("/", 1)[-1] or "download"

    return StreamingResponse(
        obj["Body"],
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/s3/upload")
async def s3_upload(
    bucket: str = Query(...),
    prefix: str = Query(""),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Upload a file to S3.

    Requires an active elevation session (checked via ``ElevationManager``).

    Args:
        bucket: Target S3 bucket.
        prefix: Key prefix (acts as the destination "folder").
        file: The uploaded file.

    Returns:
        Dict with *success*, *bucket*, *key*, and *size*.
    """
    # Elevation gate.
    if _elevation is None or _elevation.get_active() is None:
        raise HTTPException(
            status_code=403,
            detail="S3 uploads require an active elevation session",
        )

    filename = file.filename or "upload"
    key = prefix.rstrip("/") + "/" + filename if prefix else filename

    contents = await file.read()
    size = len(contents)

    try:
        _s3_client.put_object(Bucket=bucket, Key=key, Body=contents)
    except ClientError as exc:
        logger.exception("S3 upload failed for s3://%s/%s", bucket, key)
        raise HTTPException(status_code=502, detail=str(exc))

    logger.info("Uploaded %s (%d bytes) to s3://%s/%s", filename, size, bucket, key)
    return {"success": True, "bucket": bucket, "key": key, "size": size}
