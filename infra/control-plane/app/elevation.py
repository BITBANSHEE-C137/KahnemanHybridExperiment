"""Elevation state machine and STS credential management.

Implements a request-approve/deny workflow for temporary AWS privilege
escalation. Elevations move through a state machine:

    PENDING -> APPROVED -> ACTIVE -> EXPIRED
    PENDING -> DENIED

When an elevation is approved, STS AssumeRole is called and temporary
credentials are written to ~/.aws/credentials under the [elevated] profile.
On expiry, those credentials are revoked (removed from the file).
"""

import configparser
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import boto3
import httpx
from botocore.exceptions import ClientError


_ACCOUNT_ID = "004507070771"
_ROLE_ARN = f"arn:aws:iam::{_ACCOUNT_ID}:role/LabAdminRole"
_EXTERNAL_ID = "ml-lab-elevation"

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS elevations (
    id TEXT PRIMARY KEY,
    requested_at TEXT,
    decided_at TEXT,
    expires_at TEXT,
    status TEXT CHECK(status IN ('PENDING','APPROVED','ACTIVE','DENIED','EXPIRED')),
    action TEXT,
    justification TEXT,
    duration_minutes INTEGER DEFAULT 60,
    decided_by TEXT,
    sts_access_key TEXT,
    sts_session_token TEXT
)
"""


class ElevationManager:
    """Manages privilege elevation requests and temporary STS credentials.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: str = "elevations.db") -> None:
        """Initializes the ElevationManager and creates the DB table.

        Args:
            db_path: Filesystem path for the SQLite database.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Creates the elevations table if it does not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(_CREATE_TABLE_SQL)
            conn.commit()

    def _row_to_dict(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict[str, Any]:
        """Converts a sqlite3 row to a dictionary.

        Args:
            cursor: The cursor that produced the row.
            row: The row tuple.

        Returns:
            A dict mapping column names to values.
        """
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    def request(
        self,
        action: str,
        justification: str,
        duration_minutes: int = 60,
    ) -> dict[str, Any]:
        """Creates a new PENDING elevation request.

        Args:
            action: The privileged action being requested (e.g., "terminate-instance").
            justification: Human-readable reason for the elevation.
            duration_minutes: How long the elevated credentials should last.

        Returns:
            Dict with the elevation id and details.
        """
        elevation_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO elevations
                   (id, requested_at, status, action, justification, duration_minutes)
                   VALUES (?, ?, 'PENDING', ?, ?, ?)""",
                (elevation_id, now, action, justification, duration_minutes),
            )
            conn.commit()

        record = {
            "id": elevation_id,
            "requested_at": now,
            "status": "PENDING",
            "action": action,
            "justification": justification,
            "duration_minutes": duration_minutes,
        }

        self._send_telegram(
            f"Elevation requested\n"
            f"Action: {action}\n"
            f"Justification: {justification}\n"
            f"Duration: {duration_minutes}m\n"
            f"ID: {elevation_id}"
        )

        return record

    def approve(self, elevation_id: str, user_email: str) -> dict[str, Any]:
        """Approves a PENDING elevation and provisions STS credentials.

        Transitions PENDING -> APPROVED, calls STS AssumeRole, writes
        temporary credentials to ~/.aws/credentials, then transitions
        to ACTIVE.

        Args:
            elevation_id: The UUID of the elevation to approve.
            user_email: Email of the approving user (from Cloudflare JWT).

        Returns:
            Dict with the updated elevation details.

        Raises:
            ValueError: If the elevation is not found or not in PENDING status.
            ClientError: If STS AssumeRole fails.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            row = conn.execute(
                "SELECT * FROM elevations WHERE id = ?", (elevation_id,)
            ).fetchone()

        if not row:
            raise ValueError(f"Elevation {elevation_id} not found")
        if row["status"] != "PENDING":
            raise ValueError(
                f"Elevation {elevation_id} is {row['status']}, expected PENDING"
            )

        now = datetime.now(timezone.utc)
        duration = row["duration_minutes"]
        expires_at = now + timedelta(minutes=duration)

        # STS AssumeRole
        sts = boto3.client("sts")
        response = sts.assume_role(
            RoleArn=_ROLE_ARN,
            RoleSessionName=f"elevation-{elevation_id[:8]}",
            ExternalId=_EXTERNAL_ID,
            DurationSeconds=duration * 60,
        )
        creds = response["Credentials"]

        self._write_credentials(
            access_key=creds["AccessKeyId"],
            secret_key=creds["SecretAccessKey"],
            session_token=creds["SessionToken"],
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE elevations
                   SET status = 'ACTIVE',
                       decided_at = ?,
                       expires_at = ?,
                       decided_by = ?,
                       sts_access_key = ?,
                       sts_session_token = ?
                   WHERE id = ?""",
                (
                    now.isoformat(),
                    expires_at.isoformat(),
                    user_email,
                    creds["AccessKeyId"],
                    creds["SessionToken"],
                    elevation_id,
                ),
            )
            conn.commit()

        self._send_telegram(
            f"Elevation APPROVED by {user_email}\n"
            f"Action: {row['action']}\n"
            f"Expires: {expires_at.isoformat()}\n"
            f"ID: {elevation_id}"
        )

        return {
            "id": elevation_id,
            "status": "ACTIVE",
            "decided_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "decided_by": user_email,
            "action": row["action"],
        }

    def deny(self, elevation_id: str, user_email: str) -> dict[str, Any]:
        """Denies a PENDING elevation request.

        Args:
            elevation_id: The UUID of the elevation to deny.
            user_email: Email of the denying user.

        Returns:
            Dict with the updated elevation details.

        Raises:
            ValueError: If the elevation is not found or not in PENDING status.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            row = conn.execute(
                "SELECT * FROM elevations WHERE id = ?", (elevation_id,)
            ).fetchone()

        if not row:
            raise ValueError(f"Elevation {elevation_id} not found")
        if row["status"] != "PENDING":
            raise ValueError(
                f"Elevation {elevation_id} is {row['status']}, expected PENDING"
            )

        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE elevations
                   SET status = 'DENIED', decided_at = ?, decided_by = ?
                   WHERE id = ?""",
                (now, user_email, elevation_id),
            )
            conn.commit()

        self._send_telegram(
            f"Elevation DENIED by {user_email}\n"
            f"Action: {row['action']}\n"
            f"ID: {elevation_id}"
        )

        return {
            "id": elevation_id,
            "status": "DENIED",
            "decided_at": now,
            "decided_by": user_email,
            "action": row["action"],
        }

    def get_pending(self) -> list[dict[str, Any]]:
        """Returns all elevations in PENDING status.

        Returns:
            List of elevation dicts.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            rows = conn.execute(
                "SELECT * FROM elevations WHERE status = 'PENDING' ORDER BY requested_at DESC"
            ).fetchall()
        return rows

    def get_active(self) -> Optional[dict[str, Any]]:
        """Returns the current ACTIVE elevation, if any.

        Returns:
            The active elevation dict, or None.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            row = conn.execute(
                "SELECT * FROM elevations WHERE status = 'ACTIVE' ORDER BY decided_at DESC LIMIT 1"
            ).fetchone()
        return row

    def get_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Returns the most recent elevations regardless of status.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of elevation dicts ordered by requested_at descending.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            rows = conn.execute(
                "SELECT * FROM elevations ORDER BY requested_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return rows

    def check_expiry(self) -> None:
        """Checks ACTIVE elevations and expires any that have passed their expiry time.

        For each expired elevation, removes the [elevated] profile from
        ~/.aws/credentials and transitions the status to EXPIRED.
        """
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._row_to_dict
            active = conn.execute(
                "SELECT * FROM elevations WHERE status = 'ACTIVE'"
            ).fetchall()

        for elev in active:
            if elev["expires_at"] and elev["expires_at"] <= now:
                self._revoke_credentials()
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "UPDATE elevations SET status = 'EXPIRED' WHERE id = ?",
                        (elev["id"],),
                    )
                    conn.commit()

                self._send_telegram(
                    f"Elevation EXPIRED\n"
                    f"Action: {elev['action']}\n"
                    f"ID: {elev['id']}"
                )

    def _send_telegram(self, message: str) -> None:
        """Sends a notification message via Telegram bot API.

        Args:
            message: The message text to send.
        """
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not bot_token or not chat_id:
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            with httpx.Client(timeout=10.0) as client:
                client.post(url, json={"chat_id": chat_id, "text": message})
        except httpx.HTTPError:
            pass  # Best-effort notification

    def _write_credentials(
        self,
        access_key: str,
        secret_key: str,
        session_token: str,
    ) -> None:
        """Writes temporary STS credentials to ~/.aws/credentials [elevated] profile.

        Args:
            access_key: AWS access key ID.
            secret_key: AWS secret access key.
            session_token: AWS session token.
        """
        creds_path = Path.home() / ".aws" / "credentials"
        creds_path.parent.mkdir(parents=True, exist_ok=True)

        config = configparser.ConfigParser()
        if creds_path.exists():
            config.read(str(creds_path))

        if not config.has_section("elevated"):
            config.add_section("elevated")

        config.set("elevated", "aws_access_key_id", access_key)
        config.set("elevated", "aws_secret_access_key", secret_key)
        config.set("elevated", "aws_session_token", session_token)

        with open(creds_path, "w") as f:
            config.write(f)

    def _revoke_credentials(self) -> None:
        """Removes the [elevated] profile from ~/.aws/credentials."""
        creds_path = Path.home() / ".aws" / "credentials"
        if not creds_path.exists():
            return

        config = configparser.ConfigParser()
        config.read(str(creds_path))

        if config.has_section("elevated"):
            config.remove_section("elevated")
            with open(creds_path, "w") as f:
                config.write(f)
