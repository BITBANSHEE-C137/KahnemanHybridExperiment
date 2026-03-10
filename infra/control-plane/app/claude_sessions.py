"""Claude Code session management API.

Reads session data from ~/.claude/projects/ and provides list/delete
operations. Resuming a session is handled client-side by sending a
``claude --resume <id>`` command to the terminal WebSocket.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger("control-plane.claude-sessions")

router = APIRouter(prefix="/api/claude")

CLAUDE_DIR = "/home/claude-operator/.claude"


def _decode_project_dir(encoded: str) -> str:
    """Convert encoded project directory name back to a path.

    Claude Code encodes CWD by replacing ``/`` with ``-``.
    """
    if not encoded or encoded == "-":
        return "/"
    return encoded.replace("-", "/")


def _parse_session(fpath: str, session_id: str, cwd: str) -> dict[str, Any] | None:
    """Parse a session JSONL file and extract metadata."""
    first_ts: str | None = None
    last_ts: str | None = None
    user_count = 0
    assistant_count = 0
    model: str | None = None
    last_user_message: str | None = None

    with open(fpath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = obj.get("type")
            ts = obj.get("timestamp")

            if ts:
                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts

            if msg_type == "user":
                user_count += 1
                msg = obj.get("message", {})
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    last_user_message = content.strip()
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "").strip()
                            if text:
                                last_user_message = text
                            break

            elif msg_type == "assistant":
                assistant_count += 1
                msg = obj.get("message", {})
                if not model and msg.get("model"):
                    model = msg["model"]

    if user_count == 0 and assistant_count == 0:
        return None

    size = os.path.getsize(fpath)
    project_name = cwd.rstrip("/").split("/")[-1] if cwd and cwd != "/" else "root"

    preview = None
    if last_user_message:
        preview = (last_user_message[:120] + "...") if len(last_user_message) > 120 else last_user_message

    return {
        "id": session_id,
        "cwd": cwd,
        "project": project_name,
        "first_active": first_ts,
        "last_active": last_ts,
        "user_messages": user_count,
        "assistant_messages": assistant_count,
        "model": model,
        "size": size,
        "preview": preview,
    }


def _get_sessions() -> list[dict[str, Any]]:
    """Scan Claude Code session files and return metadata."""
    projects_dir = os.path.join(CLAUDE_DIR, "projects")
    if not os.path.isdir(projects_dir):
        return []

    sessions: list[dict[str, Any]] = []

    for proj_dir_name in os.listdir(projects_dir):
        proj_path = os.path.join(projects_dir, proj_dir_name)
        if not os.path.isdir(proj_path):
            continue

        cwd = _decode_project_dir(proj_dir_name)

        for fname in os.listdir(proj_path):
            if not fname.endswith(".jsonl"):
                continue

            session_id = fname[:-6]  # strip .jsonl
            fpath = os.path.join(proj_path, fname)

            try:
                session = _parse_session(fpath, session_id, cwd)
                if session:
                    sessions.append(session)
            except Exception as exc:
                logger.warning("Failed to parse session %s: %s", fpath, exc)

    sessions.sort(key=lambda s: s.get("last_active") or "", reverse=True)
    return sessions


def _is_claude_running() -> bool:
    """Check if a Claude Code process is running under claude-operator."""
    try:
        result = subprocess.run(
            ["pgrep", "-c", "-u", "claude-operator", "-f", "claude"],
            capture_output=True, text=True, timeout=5,
        )
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        return count > 0
    except Exception:
        return False


@router.get("/sessions")
async def list_sessions() -> dict[str, Any]:
    """List all Claude Code sessions with metadata."""
    sessions = _get_sessions()
    running = _is_claude_running()
    return {
        "sessions": sessions,
        "claude_running": running,
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, Any]:
    """Delete a Claude Code session file."""
    projects_dir = os.path.join(CLAUDE_DIR, "projects")
    if not os.path.isdir(projects_dir):
        raise HTTPException(status_code=404, detail="No sessions directory")

    for proj_dir_name in os.listdir(projects_dir):
        proj_path = os.path.join(projects_dir, proj_dir_name)
        if not os.path.isdir(proj_path):
            continue
        fpath = os.path.join(proj_path, session_id + ".jsonl")
        if os.path.exists(fpath):
            os.remove(fpath)
            logger.info("Deleted session %s from %s", session_id, proj_path)
            return {"success": True}

    raise HTTPException(status_code=404, detail="Session not found")
