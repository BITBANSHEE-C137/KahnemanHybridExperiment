"""FastAPI application for the ML Lab Control Plane.

Serves the control plane dashboard and API for lab status queries
and privilege elevation management. Runs behind cloudflared and
ttyd's WebSocket proxy on the GPU instance.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import CloudflareAuth
from elevation import ElevationManager
from lab_status import LabStatus

logger = logging.getLogger("control-plane")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# --- Globals initialized at startup ---
auth: CloudflareAuth
elevation: ElevationManager
lab_status: LabStatus
_start_time: float


# --- Pydantic models ---

class ElevationRequest(BaseModel):
    """Request body for creating a new elevation request.

    Attributes:
        action: The privileged action being requested.
        justification: Human-readable reason for the elevation.
        duration_minutes: How long the elevated credentials should last.
    """
    action: str
    justification: str
    duration_minutes: int = 60


# --- Background task ---

async def expiry_checker() -> None:
    """Periodically checks for expired elevations and revokes credentials.

    Runs every 30 seconds in an asyncio loop. Exceptions are caught
    and logged to prevent the task from dying.
    """
    while True:
        try:
            elevation.check_expiry()
        except Exception:
            logger.exception("Error in expiry checker")
        await asyncio.sleep(30)


# --- Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown.

    On startup: initializes auth, elevation manager, lab status,
    and starts the background expiry checker task.
    """
    global auth, elevation, lab_status, _start_time

    _start_time = time.time()

    auth = CloudflareAuth()
    elevation = ElevationManager()
    lab_status = LabStatus()

    logger.info("ML Lab Control Plane starting up")
    logger.info("Elevation DB: %s", elevation.db_path)

    task = asyncio.create_task(expiry_checker())
    logger.info("Background expiry checker started")

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    logger.info("ML Lab Control Plane shut down")


# --- App ---

app = FastAPI(title="ML Lab Control Plane", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Routes ---

@app.get("/")
async def index() -> FileResponse:
    """Serves the control plane dashboard."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health() -> dict[str, Any]:
    """Returns basic health check info.

    Returns:
        Dict with status, IAM role, and uptime in seconds.
    """
    return {
        "status": "ok",
        "role": "LabOperatorRole",
        "uptime": round(time.time() - _start_time, 1),
    }


@app.get("/api/lab/status")
async def get_lab_status() -> dict[str, Any]:
    """Returns combined fleet, training, and cost status.

    Returns:
        Full lab status dict from LabStatus.get_full_status().
    """
    return lab_status.get_full_status()


@app.get("/api/elevation/pending")
async def get_pending() -> list[dict[str, Any]]:
    """Returns all pending elevation requests.

    Returns:
        List of pending elevation dicts.
    """
    return elevation.get_pending()


@app.post("/api/elevation/request")
async def request_elevation(body: ElevationRequest) -> dict[str, Any]:
    """Creates a new elevation request. No auth required.

    This endpoint is called locally by Claude Code and does not
    require Cloudflare Access authentication.

    Args:
        body: The elevation request details.

    Returns:
        The created elevation dict with id and status.
    """
    return elevation.request(
        action=body.action,
        justification=body.justification,
        duration_minutes=body.duration_minutes,
    )


@app.post("/api/elevation/approve/{elevation_id}")
async def approve_elevation(
    elevation_id: str,
    request: Request,
    user: dict[str, Any] = Depends(lambda r: auth.get_authenticated_user(r)),
) -> dict[str, Any]:
    """Approves a pending elevation. Requires Cloudflare Access JWT.

    Args:
        elevation_id: UUID of the elevation to approve.
        request: The incoming request (for auth extraction).
        user: Authenticated user claims from Cloudflare Access.

    Returns:
        The updated elevation dict.

    Raises:
        HTTPException: 400 if the elevation cannot be approved.
    """
    try:
        return elevation.approve(elevation_id, user["email"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/elevation/deny/{elevation_id}")
async def deny_elevation(
    elevation_id: str,
    request: Request,
    user: dict[str, Any] = Depends(lambda r: auth.get_authenticated_user(r)),
) -> dict[str, Any]:
    """Denies a pending elevation. Requires Cloudflare Access JWT.

    Args:
        elevation_id: UUID of the elevation to deny.
        request: The incoming request (for auth extraction).
        user: Authenticated user claims from Cloudflare Access.

    Returns:
        The updated elevation dict.

    Raises:
        HTTPException: 400 if the elevation cannot be denied.
    """
    try:
        return elevation.deny(elevation_id, user["email"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/elevation/history")
async def get_history() -> list[dict[str, Any]]:
    """Returns the last 10 elevation records.

    Returns:
        List of elevation dicts ordered by most recent first.
    """
    return elevation.get_history()


@app.get("/api/elevation/active")
async def get_active() -> dict[str, Any]:
    """Returns the currently active elevation, if any.

    Returns:
        The active elevation dict, or None.
    """
    active = elevation.get_active()
    return active if active else {}
