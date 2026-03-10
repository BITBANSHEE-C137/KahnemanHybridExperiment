"""iCloud Drive authentication and mount management.

Drives rclone's iCloud auth flow via pseudo-terminal so the web UI
can collect Apple ID + password + 2FA code and feed them to rclone.
On success the trust token is saved to rclone.conf and the FUSE mount
is (re)started.
"""

from __future__ import annotations

import asyncio
import logging
import os
import pty
import select
import signal
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("control-plane.icloud")

router = APIRouter(prefix="/api/icloud", tags=["icloud"])

RCLONE_CONFIG = Path("/home/claude-operator/.config/rclone/rclone.conf")
MOUNT_POINT = Path("/home/claude-operator/icloud")
RCLONE_BIN = "/usr/bin/rclone"


# ---------------------------------------------------------------------------
# Auth session state (singleton — one auth at a time)
# ---------------------------------------------------------------------------

class _AuthSession:
    """Manages a single rclone interactive auth process."""

    def __init__(self) -> None:
        self.master_fd: int | None = None
        self.child_pid: int | None = None
        self.output: bytes = b""
        self.state: str = "idle"  # idle | awaiting_2fa | authenticated | error

    def cleanup(self) -> None:
        """Kill child process and close pty."""
        if self.child_pid:
            try:
                os.kill(self.child_pid, signal.SIGTERM)
                os.waitpid(self.child_pid, os.WNOHANG)
            except (OSError, ChildProcessError):
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        self.master_fd = None
        self.child_pid = None
        self.output = b""


_session = _AuthSession()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SignInRequest(BaseModel):
    apple_id: str
    password: str


class VerifyRequest(BaseModel):
    code: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_pty(fd: int, timeout: float) -> bytes:
    """Read from *fd* until *timeout* seconds elapse."""
    buf = b""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        remaining = end - time.monotonic()
        if remaining <= 0:
            break
        r, _, _ = select.select([fd], [], [], min(remaining, 0.5))
        if r:
            try:
                chunk = os.read(fd, 4096)
                if not chunk:
                    break
                buf += chunk
            except OSError:
                break
    return buf


def _start_rclone_auth() -> str:
    """Fork ``rclone lsd icloud:`` with a pty, wait for the 2FA prompt.

    Returns the resulting auth state string.
    """
    _session.cleanup()

    pid, fd = pty.fork()
    if pid == 0:
        # Child — exec rclone
        os.execvp(RCLONE_BIN, [
            RCLONE_BIN, "lsd", "icloud:",
            "--config", str(RCLONE_CONFIG),
        ])
        os._exit(1)

    _session.child_pid = pid
    _session.master_fd = fd
    _session.output = b""

    # Read output for up to 20 s looking for a 2FA prompt
    end = time.monotonic() + 20
    while time.monotonic() < end:
        remaining = end - time.monotonic()
        r, _, _ = select.select([fd], [], [], min(remaining, 0.5))
        if r:
            try:
                chunk = os.read(fd, 4096)
                _session.output += chunk
            except OSError:
                break

            lower = _session.output.lower()
            if b"code" in lower or b"2fa" in lower or b"verification" in lower:
                _session.state = "awaiting_2fa"
                return "awaiting_2fa"

        # Check if child already exited (auth error / bad creds)
        try:
            wpid, status = os.waitpid(pid, os.WNOHANG)
            if wpid != 0:
                _session.state = "error"
                return "error"
        except ChildProcessError:
            _session.state = "error"
            return "error"

    # Timeout — Apple may still have sent 2FA push even if prompt text
    # didn't match our keywords, so optimistically report awaiting_2fa.
    _session.state = "awaiting_2fa"
    return "awaiting_2fa"


def _submit_2fa_code(code: str) -> tuple[bool, str]:
    """Write *code* to the rclone pty and wait for completion.

    Returns ``(success, combined_output)``.
    """
    if _session.master_fd is None:
        return False, "No active auth session"

    try:
        os.write(_session.master_fd, f"{code}\n".encode())
    except OSError as exc:
        _session.cleanup()
        return False, f"Failed to send code: {exc}"

    # Wait for the child to exit (up to 30 s)
    try:
        for _ in range(60):
            try:
                wpid, status = os.waitpid(_session.child_pid, os.WNOHANG)
            except ChildProcessError:
                break
            if wpid != 0:
                exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else -1
                # Drain remaining output
                try:
                    tail = _read_pty(_session.master_fd, timeout=2)
                    _session.output += tail
                except Exception:
                    pass
                fd = _session.master_fd
                _session.master_fd = None
                _session.child_pid = None
                try:
                    os.close(fd)
                except OSError:
                    pass
                return exit_code == 0, _session.output.decode(errors="replace")
            time.sleep(0.5)
    except Exception:
        pass

    # Timeout
    _session.cleanup()
    return False, "Timed out waiting for rclone to finish"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/status")
async def icloud_status() -> dict:
    """Return current iCloud mount status."""
    mounted = os.path.ismount(str(MOUNT_POINT))
    has_token = False
    if RCLONE_CONFIG.exists():
        try:
            text = RCLONE_CONFIG.read_text()
            has_token = "trust_token" in text and len(
                [l for l in text.splitlines() if l.strip().startswith("trust_token") and "=" in l and l.split("=", 1)[1].strip()]
            ) > 0
        except Exception:
            pass
    return {
        "mounted": mounted,
        "has_token": has_token,
        "auth_state": _session.state,
    }


@router.post("/auth/start")
async def start_auth(req: SignInRequest) -> dict:
    """Write rclone config and kick off Apple auth (triggers 2FA push)."""
    # Write rclone config with credentials
    RCLONE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    RCLONE_CONFIG.write_text(
        "[icloud]\n"
        "type = iclouddrive\n"
        f"apple_id = {req.apple_id}\n"
        f"password = {req.password}\n"
    )
    os.chmod(str(RCLONE_CONFIG), 0o600)

    # Stop any existing mount
    proc = await asyncio.create_subprocess_exec(
        "sudo", "systemctl", "stop", "rclone-icloud",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()

    # Start rclone auth (blocking pty ops) in a thread
    state = await asyncio.to_thread(_start_rclone_auth)

    if state == "error":
        output = _session.output.decode(errors="replace")
        _session.cleanup()
        raise HTTPException(401, detail=f"Sign-in failed: {output}")

    return {
        "status": "2fa_required",
        "message": "Enter the verification code from your Apple device",
    }


@router.post("/auth/verify")
async def verify_2fa(req: VerifyRequest) -> dict:
    """Submit the 2FA code, wait for rclone to complete, start mount."""
    if _session.state != "awaiting_2fa":
        raise HTTPException(400, detail="No active auth session awaiting 2FA")

    success, output = await asyncio.to_thread(_submit_2fa_code, req.code)

    if not success:
        _session.state = "error"
        raise HTTPException(401, detail=f"Verification failed: {output}")

    _session.state = "authenticated"

    # Start the FUSE mount
    proc = await asyncio.create_subprocess_exec(
        "sudo", "systemctl", "start", "rclone-icloud",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    # Wait for mount to appear (up to 10 s)
    for _ in range(10):
        if os.path.ismount(str(MOUNT_POINT)):
            return {"status": "mounted"}
        await asyncio.sleep(1)

    return {"status": "auth_ok", "message": "Authenticated. Mount may take a moment."}


@router.post("/unmount")
async def unmount() -> dict:
    """Unmount iCloud drive."""
    proc = await asyncio.create_subprocess_exec(
        "sudo", "systemctl", "stop", "rclone-icloud",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    _session.state = "idle"
    return {"status": "unmounted"}
