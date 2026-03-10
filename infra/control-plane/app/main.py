"""FastAPI application for the ML Lab Control Plane.

Serves the control plane dashboard and API for lab status queries,
multi-project AWS resource discovery, task management, privilege
elevation management, and file browsing. Runs behind cloudflared and ttyd's WebSocket
proxy on the control plane instance.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import CloudflareAuth
from aws_discovery import AWSDiscovery
from elevation import ElevationManager
from filesystem import router as fs_router, set_elevation_manager
from lab_status import LabStatus
from taskboard import TaskBoard

logger = logging.getLogger("control-plane")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# --- Globals initialized at startup ---
auth: CloudflareAuth
elevation: ElevationManager
lab_status: LabStatus
discovery: AWSDiscovery
taskboard: TaskBoard
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


class TaskCreate(BaseModel):
    """Request body for creating a new task.

    Attributes:
        title: The task title.
        description: Optional task description.
    """
    title: str
    description: str = ""


class TaskUpdate(BaseModel):
    """Request body for updating a task.

    Attributes:
        title: New title (optional).
        description: New description (optional).
        status: New status: todo, in_progress, or done (optional).
        position: New sort position (optional).
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    position: Optional[int] = None


class NotesSave(BaseModel):
    """Request body for saving project notes.

    Attributes:
        content: The notes content.
    """
    content: str


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
    AWS discovery, task board, and starts the background expiry checker.
    """
    global auth, elevation, lab_status, discovery, taskboard, _start_time

    _start_time = time.time()

    auth = CloudflareAuth()
    elevation = ElevationManager()
    lab_status = LabStatus()
    discovery = AWSDiscovery()
    taskboard = TaskBoard()

    # Share the elevation manager with the filesystem module.
    set_elevation_manager(elevation)

    logger.info("ML Lab Control Plane starting up")
    logger.info("Elevation DB: %s", elevation.db_path)
    logger.info("TaskBoard DB: %s", taskboard.db_path)

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
app.include_router(fs_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Routes: Core ---

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


# --- Routes: Lab Status (existing) ---

@app.get("/api/lab/status")
async def get_lab_status() -> dict[str, Any]:
    """Returns combined fleet, training, and cost status.

    Returns:
        Full lab status dict from LabStatus.get_full_status().
    """
    return lab_status.get_full_status()


# --- Routes: Multi-Project Discovery ---

@app.get("/api/projects")
async def get_projects() -> list[dict[str, Any]]:
    """Returns all projects with resource counts.

    Returns:
        List of project summary dicts.
    """
    return discovery.get_all_projects_summary()


@app.get("/api/projects/{name}/resources")
async def get_project_resources(name: str) -> dict[str, Any]:
    """Returns all resources for one project.

    Args:
        name: The project name.

    Returns:
        Dict with all resource types for the project.
    """
    return discovery.get_project_resources(name)


@app.get("/api/resources/ec2")
async def get_ec2_instances() -> list[dict[str, Any]]:
    """Returns all EC2 instances across projects.

    Returns:
        List of instance dicts.
    """
    return discovery.get_ec2_instances()


@app.get("/api/resources/lambda")
async def get_lambda_functions() -> list[dict[str, Any]]:
    """Returns all Lambda functions with 24h metrics.

    Returns:
        List of function dicts with invocation and error counts.
    """
    return discovery.get_lambda_functions()


@app.get("/api/resources/s3")
async def get_s3_buckets() -> list[dict[str, Any]]:
    """Returns all S3 buckets with metadata.

    Returns:
        List of bucket dicts.
    """
    return discovery.get_s3_buckets()


@app.get("/api/resources/cloudfront")
async def get_cloudfront_distributions() -> list[dict[str, Any]]:
    """Returns all CloudFront distributions.

    Returns:
        List of distribution dicts.
    """
    return discovery.get_cloudfront_distributions()


@app.get("/api/resources/route53")
async def get_route53_zones() -> list[dict[str, Any]]:
    """Returns all Route53 zones.

    Returns:
        List of zone dicts.
    """
    return discovery.get_route53_zones()


@app.get("/api/cost/summary")
async def get_cost_summary() -> dict[str, Any]:
    """Returns cost summary from CloudWatch billing metrics.

    Returns:
        Dict with month-to-date cost estimate.
    """
    return discovery.get_cost_summary()


# --- Routes: Task Board ---

@app.get("/api/tasks/{project}")
async def get_tasks(project: str) -> dict[str, list[dict[str, Any]]]:
    """Returns all tasks for a project, grouped by status.

    Args:
        project: The project name, or 'all' for all projects.

    Returns:
        Dict with 'todo', 'in_progress', 'done' task lists.
    """
    if project == "all":
        return taskboard.list_all_tasks()
    return taskboard.list_tasks(project)


@app.post("/api/tasks/{project}")
async def create_task(project: str, body: TaskCreate) -> dict[str, Any]:
    """Creates a new task in TODO status.

    Args:
        project: The project name.
        body: Task creation body with title and description.

    Returns:
        The created task dict.
    """
    return taskboard.create_task(
        project=project, title=body.title, description=body.description
    )


@app.put("/api/tasks/{project}/{task_id}")
async def update_task(project: str, task_id: str, body: TaskUpdate) -> dict[str, Any]:
    """Updates a task's fields.

    Args:
        project: The project name (for URL consistency).
        task_id: The task UUID.
        body: Fields to update.

    Returns:
        The updated task dict.

    Raises:
        HTTPException: 404 if task not found, 400 if invalid status.
    """
    try:
        return taskboard.update_task(
            task_id=task_id,
            title=body.title,
            description=body.description,
            status=body.status,
            position=body.position,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/api/tasks/{project}/{task_id}")
async def delete_task(project: str, task_id: str) -> dict[str, Any]:
    """Deletes a task.

    Args:
        project: The project name (for URL consistency).
        task_id: The task UUID.

    Returns:
        Dict with deletion status.

    Raises:
        HTTPException: 404 if task not found.
    """
    if not taskboard.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"deleted": True, "id": task_id}


# --- Routes: Notes ---

@app.get("/api/notes/{project}")
async def get_notes(project: str) -> dict[str, Any]:
    """Returns freeform notes for a project.

    Args:
        project: The project name.

    Returns:
        Dict with project, content, and updated_at.
    """
    return taskboard.get_notes(project)


@app.post("/api/notes/{project}")
async def save_notes(project: str, body: NotesSave) -> dict[str, Any]:
    """Saves freeform notes for a project.

    Args:
        project: The project name.
        body: Notes content.

    Returns:
        Dict with project, content, and updated_at.
    """
    return taskboard.save_notes(project, body.content)




# --- Routes: Terminal Management ---

@app.post("/api/terminal/restart")
async def restart_terminal() -> dict[str, Any]:
    """Restarts the ttyd terminal service to create a fresh session.

    Returns:
        Dict with status of the restart.
    """
    import subprocess as sp
    try:
        sp.run(["sudo", "systemctl", "restart", "cc-tmux"], check=True, timeout=10)
        sp.run(["sudo", "systemctl", "restart", "ttyd"], check=True, timeout=10)
        logger.info("Terminal services restarted")
        return {"status": "ok", "message": "Terminal session restarted"}
    except sp.CalledProcessError as exc:
        logger.exception("Failed to restart terminal services")
        raise HTTPException(status_code=500, detail=f"Restart failed: {exc}")
    except sp.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Restart timed out")

import asyncio as _asyncio

import websockets as _ws
from fastapi import WebSocket as _FastAPIWebSocket
from starlette.websockets import WebSocketDisconnect as _WsDisconnect


@app.websocket("/api/shell/ws")
async def shell_ws_proxy(client: _FastAPIWebSocket) -> None:
    """Proxies WebSocket traffic to the shell ttyd instance on port 7682.

    Accepts the browser WebSocket, opens a connection to the local
    ttyd-shell, and forwards binary frames in both directions.
    """
    await client.accept(subprotocol="tty")
    try:
        async with _ws.connect(
            "ws://127.0.0.1:7682/shell/ws",
            subprotocols=["tty"],
            max_size=2**20,
        ) as backend:

            async def client_to_backend() -> None:
                try:
                    while True:
                        data = await client.receive_bytes()
                        await backend.send(data)
                except _WsDisconnect:
                    pass

            async def backend_to_client() -> None:
                try:
                    async for msg in backend:
                        if isinstance(msg, bytes):
                            await client.send_bytes(msg)
                        else:
                            await client.send_text(msg)
                except _ws.exceptions.ConnectionClosed:
                    pass

            done, pending = await _asyncio.wait(
                [
                    _asyncio.create_task(client_to_backend()),
                    _asyncio.create_task(backend_to_client()),
                ],
                return_when=_asyncio.FIRST_COMPLETED,
            )
            for t in pending:
                t.cancel()
    except Exception:
        logger.exception("Shell WebSocket proxy error")
    finally:
        try:
            await client.close()
        except Exception:
            pass


@app.post("/api/shell/restart")
async def restart_shell() -> dict[str, Any]:
    """Restarts the shell ttyd service to create a fresh session.

    Returns:
        Dict with status of the restart.
    """
    import subprocess as sp
    try:
        sp.run(["sudo", "systemctl", "restart", "cc-shell"], check=True, timeout=10)
        sp.run(["sudo", "systemctl", "restart", "ttyd-shell"], check=True, timeout=10)
        logger.info("Shell terminal services restarted")
        return {"status": "ok", "message": "Shell session restarted"}
    except sp.CalledProcessError as exc:
        logger.exception("Failed to restart shell services")
        raise HTTPException(status_code=500, detail=f"Restart failed: {exc}")
    except sp.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Restart timed out")


# --- Routes: Elevation (existing) ---

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
