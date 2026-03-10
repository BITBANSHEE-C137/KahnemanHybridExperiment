"""SQLite-backed per-project task board and freeform notes.

Provides Kanban-style task management (TODO / IN PROGRESS / DONE)
and freeform project notes, persisted in a local SQLite database.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'todo',
    position INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);

CREATE TABLE IF NOT EXISTS notes (
    project TEXT PRIMARY KEY,
    content TEXT DEFAULT '',
    updated_at TEXT
);
"""


class TaskBoard:
    """SQLite-backed task board and notes manager."""

    def __init__(self, db_path: str = "taskboard.db") -> None:
        """Initializes the task board and creates tables if needed.

        Args:
            db_path: Filesystem path for the SQLite database.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Creates the tasks and notes tables if they do not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(_SCHEMA_SQL)
            conn.commit()

    def _row_to_dict(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict[str, Any]:
        """Converts a sqlite3 row to a dictionary."""
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    def _now(self) -> str:
        """Returns the current UTC time as an ISO 8601 string."""
        return datetime.now(timezone.utc).isoformat()

    def list_tasks(
        self, project: str, status: Optional[str] = None
    ) -> dict[str, list[dict[str, Any]]]:
        """List tasks for a project, grouped by status.

        Args:
            project: The project name.
            status: Optional status filter (todo, in_progress, done).

        Returns:
            Dict with keys 'todo', 'in_progress', 'done', each a list of task dicts.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            if status:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE project = ? AND status = ? "
                    "ORDER BY position, created_at",
                    (project, status),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE project = ? "
                    "ORDER BY position, created_at",
                    (project,),
                ).fetchall()

        grouped: dict[str, list[dict[str, Any]]] = {
            "todo": [], "in_progress": [], "done": [],
        }
        for row in rows:
            s = row.get("status", "todo")
            if s in grouped:
                grouped[s].append(row)
        return grouped

    def list_all_tasks(self) -> dict[str, list[dict[str, Any]]]:
        """List all tasks across all projects, grouped by status.

        Returns:
            Dict with keys 'todo', 'in_progress', 'done'.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY project, position, created_at"
            ).fetchall()

        grouped: dict[str, list[dict[str, Any]]] = {
            "todo": [], "in_progress": [], "done": [],
        }
        for row in rows:
            s = row.get("status", "todo")
            if s in grouped:
                grouped[s].append(row)
        return grouped

    def create_task(
        self, project: str, title: str, description: str = ""
    ) -> dict[str, Any]:
        """Create a new task in TODO status.

        Args:
            project: The project name.
            title: Task title.
            description: Optional task description.

        Returns:
            The created task dict.
        """
        task_id = str(uuid4())
        now = self._now()

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM tasks "
                "WHERE project = ? AND status = 'todo'",
                (project,),
            ).fetchone()
            position = row[0] if row else 0

            conn.execute(
                "INSERT INTO tasks "
                "(id, project, title, description, status, position, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, 'todo', ?, ?, ?)",
                (task_id, project, title, description, position, now, now),
            )
            conn.commit()

        return {
            "id": task_id, "project": project, "title": title,
            "description": description, "status": "todo",
            "position": position, "created_at": now, "updated_at": now,
        }

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        position: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update a task's fields.

        Args:
            task_id: The task UUID.
            title: New title (optional).
            description: New description (optional).
            status: New status: todo, in_progress, or done (optional).
            position: New sort position (optional).

        Returns:
            The updated task dict.

        Raises:
            ValueError: If task not found or invalid status.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            existing = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if not existing:
                raise ValueError(f"Task {task_id} not found")

            updates: list[str] = []
            params: list[Any] = []
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if status is not None:
                if status not in ("todo", "in_progress", "done"):
                    raise ValueError(f"Invalid status: {status}")
                updates.append("status = ?")
                params.append(status)
            if position is not None:
                updates.append("position = ?")
                params.append(position)

            if updates:
                updates.append("updated_at = ?")
                params.append(self._now())
                params.append(task_id)
                conn.execute(
                    f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                conn.commit()

            return conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task UUID.

        Returns:
            True if a task was deleted, False if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_notes(self, project: str) -> dict[str, Any]:
        """Get freeform notes for a project.

        Args:
            project: The project name.

        Returns:
            Dict with project, content, and updated_at.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            row = conn.execute(
                "SELECT * FROM notes WHERE project = ?", (project,)
            ).fetchone()
        return row or {"project": project, "content": "", "updated_at": None}

    def save_notes(self, project: str, content: str) -> dict[str, Any]:
        """Save freeform notes for a project.

        Args:
            project: The project name.
            content: The notes content.

        Returns:
            Dict with project, content, and updated_at.
        """
        now = self._now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO notes (project, content, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(project) DO UPDATE SET "
                "content = excluded.content, updated_at = excluded.updated_at",
                (project, content, now),
            )
            conn.commit()
        return {"project": project, "content": content, "updated_at": now}
