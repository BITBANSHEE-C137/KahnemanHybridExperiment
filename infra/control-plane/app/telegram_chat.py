"""Telegram Bot API proxy for the lab control plane.

Provides endpoints to send/receive messages through the Telegram Bot API,
enabling a chat interface in the lab dashboard. Messages are stored locally
so both sent and received messages persist across page refreshes.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("control-plane.telegram")

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Persistent message store
DATA_DIR = Path("/home/claude-operator/.telegram")
MESSAGES_FILE = DATA_DIR / "messages.json"
STATE_FILE = DATA_DIR / "state.json"

# In-memory cache
_messages: list[dict] = []
_last_update_id: int = 0
_loaded: bool = False


class SendRequest(BaseModel):
    text: str


def _check_config() -> None:
    if not BOT_TOKEN or not CHAT_ID:
        raise HTTPException(503, detail="Telegram bot not configured")


def _load_store() -> None:
    """Load messages and state from disk on first access."""
    global _messages, _last_update_id, _loaded
    if _loaded:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if MESSAGES_FILE.exists():
        try:
            _messages = json.loads(MESSAGES_FILE.read_text())
        except Exception:
            _messages = []
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            _last_update_id = state.get("last_update_id", 0)
        except Exception:
            pass
    _loaded = True


def _save_store() -> None:
    """Persist messages and state to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Keep last 500 messages max
    trimmed = _messages[-500:] if len(_messages) > 500 else _messages
    MESSAGES_FILE.write_text(json.dumps(trimmed))
    STATE_FILE.write_text(json.dumps({"last_update_id": _last_update_id}))


def _add_message(msg: dict) -> None:
    """Add a message to the store if not already present."""
    # Deduplicate by message_id
    existing_ids = {m["id"] for m in _messages}
    if msg["id"] not in existing_ids:
        _messages.append(msg)
        _save_store()


def _format_update(msg: dict) -> dict:
    """Convert a Telegram message object to our format."""
    sender = msg.get("from", {})
    return {
        "id": msg["message_id"],
        "from": sender.get("first_name", sender.get("username", "Unknown")),
        "is_bot": sender.get("is_bot", False),
        "text": msg.get("text", ""),
        "date": msg.get("date", 0),
        "has_photo": bool(msg.get("photo")),
        "has_document": bool(msg.get("document")),
        "caption": msg.get("caption", ""),
    }


async def _handle_command(text: str) -> str | None:
    """Check if text is a bot command and return a reply, or None."""
    cmd = text.strip().split()[0].lower() if text.strip() else ""

    if cmd == "/status":
        try:
            import socket
            import subprocess as sp

            hostname = socket.gethostname()
            uptime = sp.run(["uptime", "-p"], capture_output=True, text=True, timeout=5).stdout.strip()
            load = sp.run(["uptime"], capture_output=True, text=True, timeout=5).stdout.strip()
            load_part = load.split("load average:")[-1].strip() if "load average:" in load else "?"
            disk = sp.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5).stdout.strip().split("\n")[-1].split()
            disk_info = f"{disk[2]}/{disk[1]} ({disk[4]})" if len(disk) >= 5 else "?"
            mem = sp.run(["free", "-h"], capture_output=True, text=True, timeout=5).stdout.strip().split("\n")
            mem_info = "?"
            if len(mem) >= 2:
                parts = mem[1].split()
                if len(parts) >= 3:
                    mem_info = f"{parts[2]}/{parts[1]}"

            return (
                f"*Control Plane Status*\n"
                f"Host: `{hostname}`\n"
                f"Uptime: {uptime}\n"
                f"Load: {load_part}\n"
                f"Memory: {mem_info}\n"
                f"Disk: {disk_info}"
            )
        except Exception as exc:
            return f"Status check failed: {exc}"

    elif cmd == "/sitrep":
        try:
            import subprocess as sp

            lines = ["*Situation Report*\n"]

            # Control plane services
            for svc in ["controlplane-api", "cloudflared", "ttyd", "ttyd-shell"]:
                result = sp.run(
                    ["systemctl", "is-active", svc],
                    capture_output=True, text=True, timeout=5,
                )
                state = result.stdout.strip()
                icon = "+" if state == "active" else "-"
                lines.append(f"`[{icon}]` {svc}: {state}")

            # Uptime
            uptime = sp.run(["uptime", "-p"], capture_output=True, text=True, timeout=5).stdout.strip()
            lines.append(f"\nUptime: {uptime}")

            return "\n".join(lines)
        except Exception as exc:
            return f"Sitrep failed: {exc}"

    elif cmd == "/help":
        return (
            "*Available Commands*\n"
            "/status — System status (host, load, memory, disk)\n"
            "/sitrep — Service health check\n"
            "/help — This message"
        )

    return None


async def _auto_reply(text: str) -> None:
    """If text is a command, send an auto-reply via the bot."""
    reply = await _handle_command(text)
    if reply is None:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API_BASE}/sendMessage",
                json={"chat_id": CHAT_ID, "text": reply, "parse_mode": "Markdown"},
            )
            data = resp.json()
            if data.get("ok"):
                msg = data["result"]
                _add_message({
                    "id": msg["message_id"],
                    "from": msg.get("from", {}).get("first_name", "Bot"),
                    "is_bot": True,
                    "text": msg.get("text", reply),
                    "date": msg["date"],
                    "has_photo": False,
                    "has_document": False,
                    "caption": "",
                })
    except Exception as exc:
        logger.warning("Auto-reply failed: %s", exc)


@router.get("/status")
async def telegram_status() -> dict[str, Any]:
    """Check Telegram bot connectivity."""
    if not BOT_TOKEN or not CHAT_ID:
        return {"configured": False, "ok": False}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE}/getMe")
            data = resp.json()
            if data.get("ok"):
                bot = data["result"]
                return {
                    "configured": True,
                    "ok": True,
                    "bot_name": bot.get("first_name", ""),
                    "bot_username": bot.get("username", ""),
                }
    except Exception as exc:
        logger.warning("Telegram status check failed: %s", exc)
    return {"configured": True, "ok": False}


@router.get("/messages")
async def get_messages() -> dict[str, Any]:
    """Poll for new messages and return any new ones since last check."""
    global _last_update_id
    _check_config()
    _load_store()

    new_messages: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params: dict[str, Any] = {
                "allowed_updates": '["message"]',
                "limit": 100,
                "timeout": 1,
            }
            if _last_update_id > 0:
                params["offset"] = _last_update_id + 1

            resp = await client.get(f"{API_BASE}/getUpdates", params=params)
            data = resp.json()

            if not data.get("ok"):
                raise HTTPException(502, detail="Telegram API error")

            for update in data.get("result", []):
                _last_update_id = max(_last_update_id, update["update_id"])
                msg = update.get("message")
                if not msg:
                    continue
                chat = msg.get("chat", {})
                if str(chat.get("id")) != CHAT_ID:
                    continue
                formatted = _format_update(msg)
                _add_message(formatted)
                new_messages.append(formatted)

                # Auto-reply to commands from non-bot users
                if not formatted["is_bot"] and formatted["text"].startswith("/"):
                    await _auto_reply(formatted["text"])

            if data.get("result"):
                _save_store()

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch Telegram messages")
        raise HTTPException(502, detail=f"Telegram fetch failed: {exc}")

    return {"new_messages": new_messages}


@router.get("/history")
async def get_history(limit: int = 100) -> dict[str, Any]:
    """Return stored message history (both sent and received)."""
    _check_config()
    _load_store()

    # Also poll for any new messages to catch up
    global _last_update_id
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params: dict[str, Any] = {
                "allowed_updates": '["message"]',
                "limit": 100,
                "timeout": 0,
            }
            if _last_update_id > 0:
                params["offset"] = _last_update_id + 1

            resp = await client.get(f"{API_BASE}/getUpdates", params=params)
            data = resp.json()

            if data.get("ok"):
                for update in data.get("result", []):
                    _last_update_id = max(_last_update_id, update["update_id"])
                    msg = update.get("message")
                    if not msg:
                        continue
                    chat = msg.get("chat", {})
                    if str(chat.get("id")) != CHAT_ID:
                        continue
                    _add_message(_format_update(msg))

                if data.get("result"):
                    _save_store()
    except Exception:
        pass  # History still returns stored messages even if poll fails

    messages = _messages[-limit:]
    return {"messages": messages}


@router.post("/send")
async def send_message(req: SendRequest) -> dict[str, Any]:
    """Send a message to the configured Telegram chat and store it."""
    _check_config()
    _load_store()

    if not req.text.strip():
        raise HTTPException(400, detail="Message text is required")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API_BASE}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": req.text,
                    "parse_mode": "Markdown",
                },
            )
            data = resp.json()

            if not data.get("ok"):
                raise HTTPException(
                    502,
                    detail=f"Telegram send failed: {data.get('description', 'Unknown error')}",
                )

            msg = data["result"]
            # Store the sent message (bot's own message)
            stored = {
                "id": msg["message_id"],
                "from": msg.get("from", {}).get("first_name", "Bot"),
                "is_bot": True,
                "text": msg.get("text", req.text),
                "date": msg["date"],
                "has_photo": False,
                "has_document": False,
                "caption": "",
            }
            _add_message(stored)

            # Handle commands sent from the lab card
            if req.text.strip().startswith("/"):
                await _auto_reply(req.text)

            return {
                "ok": True,
                "message_id": msg["message_id"],
                "date": msg["date"],
            }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to send Telegram message")
        raise HTTPException(502, detail=f"Send failed: {exc}")
