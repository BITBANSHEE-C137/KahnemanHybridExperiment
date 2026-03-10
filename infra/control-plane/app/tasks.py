"""Tasks API for the ML Lab control plane.

Simple todo-list CRUD stored as a JSON file.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("control-plane.tasks")

router = APIRouter(prefix="/api/tasks")

TASKS_FILE = "/home/claude-operator/.lab/tasks.json"


class TaskCreate(BaseModel):
    text: str


class TaskUpdate(BaseModel):
    text: str | None = None
    done: bool | None = None


def _load_tasks() -> list[dict[str, Any]]:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_tasks(tasks: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


@router.get("/list")
async def list_tasks() -> dict[str, Any]:
    """Return all tasks, newest first."""
    return {"tasks": _load_tasks()}


@router.post("/create")
async def create_task(body: TaskCreate) -> dict[str, Any]:
    """Create a new task."""
    tasks = _load_tasks()
    task: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "text": body.text,
        "done": False,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    tasks.insert(0, task)
    _save_tasks(tasks)
    return {"success": True, "task": task}


@router.put("/{task_id}")
async def update_task(task_id: str, body: TaskUpdate) -> dict[str, Any]:
    """Update a task (text or done status)."""
    tasks = _load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if body.text is not None:
                task["text"] = body.text
            if body.done is not None:
                task["done"] = body.done
            _save_tasks(tasks)
            return {"success": True, "task": task}
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}")
async def delete_task(task_id: str) -> dict[str, Any]:
    """Delete a task."""
    tasks = _load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == original_len:
        raise HTTPException(status_code=404, detail="Task not found")
    _save_tasks(tasks)
    return {"success": True}
