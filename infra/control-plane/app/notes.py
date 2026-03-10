"""Notes API for the ML Lab control plane.

Simple CRUD for persistent notes stored as a JSON file.
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

logger = logging.getLogger("control-plane.notes")

router = APIRouter(prefix="/api/notes")

NOTES_FILE = "/home/claude-operator/.lab/notes.json"


class NoteCreate(BaseModel):
    title: str = ""
    content: str = ""


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


def _load_notes() -> list[dict[str, Any]]:
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_notes(notes: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


@router.get("/list")
async def list_notes() -> dict[str, Any]:
    """Return all notes, newest first."""
    return {"notes": _load_notes()}


@router.post("/create")
async def create_note(body: NoteCreate) -> dict[str, Any]:
    """Create a new note."""
    notes = _load_notes()
    now = datetime.now(timezone.utc).isoformat()
    note: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "title": body.title,
        "content": body.content,
        "created": now,
        "modified": now,
    }
    notes.insert(0, note)
    _save_notes(notes)
    return {"success": True, "note": note}


@router.put("/{note_id}")
async def update_note(note_id: str, body: NoteUpdate) -> dict[str, Any]:
    """Update an existing note."""
    notes = _load_notes()
    for note in notes:
        if note["id"] == note_id:
            if body.title is not None:
                note["title"] = body.title
            if body.content is not None:
                note["content"] = body.content
            note["modified"] = datetime.now(timezone.utc).isoformat()
            _save_notes(notes)
            return {"success": True, "note": note}
    raise HTTPException(status_code=404, detail="Note not found")


@router.delete("/{note_id}")
async def delete_note(note_id: str) -> dict[str, Any]:
    """Delete a note."""
    notes = _load_notes()
    original_len = len(notes)
    notes = [n for n in notes if n["id"] != note_id]
    if len(notes) == original_len:
        raise HTTPException(status_code=404, detail="Note not found")
    _save_notes(notes)
    return {"success": True}
