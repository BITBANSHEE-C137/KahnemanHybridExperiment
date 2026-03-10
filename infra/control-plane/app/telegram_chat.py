"""Telegram Bot API proxy for the lab control plane.

Provides endpoints to send/receive messages through the Telegram Bot API,
enabling a chat interface in the lab dashboard. Messages are fetched via
long-polling (getUpdates) and sent via sendMessage.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("control-plane.telegram")

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Track last update_id to avoid re-fetching old messages
_last_update_id: int = 0


class SendRequest(BaseModel):
    text: str


def _check_config() -> None:
    """Raise 503 if bot token or chat ID is not configured."""
    if not BOT_TOKEN or not CHAT_ID:
        raise HTTPException(503, detail="Telegram bot not configured")


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
async def get_messages(limit: int = 50) -> dict[str, Any]:
    """Fetch recent messages from the bot's chat.

    Uses getUpdates with offset to fetch new messages since last check.
    Returns messages in chronological order.
    """
    global _last_update_id
    _check_config()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params: dict[str, Any] = {"allowed_updates": '["message"]', "limit": min(limit, 100)}
            if _last_update_id > 0:
                params["offset"] = _last_update_id + 1

            resp = await client.get(f"{API_BASE}/getUpdates", params=params)
            data = resp.json()

            if not data.get("ok"):
                raise HTTPException(502, detail="Telegram API error")

            messages = []
            for update in data.get("result", []):
                _last_update_id = max(_last_update_id, update["update_id"])
                msg = update.get("message")
                if not msg:
                    continue
                # Only include messages from our chat
                chat = msg.get("chat", {})
                if str(chat.get("id")) != CHAT_ID:
                    continue
                sender = msg.get("from", {})
                messages.append({
                    "id": msg["message_id"],
                    "from": sender.get("first_name", sender.get("username", "Unknown")),
                    "is_bot": sender.get("is_bot", False),
                    "text": msg.get("text", ""),
                    "date": msg.get("date", 0),
                    "has_photo": bool(msg.get("photo")),
                    "has_document": bool(msg.get("document")),
                    "caption": msg.get("caption", ""),
                })

            return {"messages": messages, "last_update_id": _last_update_id}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch Telegram messages")
        raise HTTPException(502, detail=f"Telegram fetch failed: {exc}")


@router.get("/history")
async def get_history(limit: int = 50) -> dict[str, Any]:
    """Fetch message history without advancing the offset.

    On first load, fetches the most recent messages regardless of offset.
    Useful for populating the chat on page load.
    """
    _check_config()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch without offset to get recent messages
            params: dict[str, Any] = {"allowed_updates": '["message"]', "limit": min(limit, 100)}
            resp = await client.get(f"{API_BASE}/getUpdates", params=params)
            data = resp.json()

            if not data.get("ok"):
                raise HTTPException(502, detail="Telegram API error")

            messages = []
            for update in data.get("result", []):
                msg = update.get("message")
                if not msg:
                    continue
                chat = msg.get("chat", {})
                if str(chat.get("id")) != CHAT_ID:
                    continue
                sender = msg.get("from", {})
                messages.append({
                    "id": msg["message_id"],
                    "from": sender.get("first_name", sender.get("username", "Unknown")),
                    "is_bot": sender.get("is_bot", False),
                    "text": msg.get("text", ""),
                    "date": msg.get("date", 0),
                    "has_photo": bool(msg.get("photo")),
                    "has_document": bool(msg.get("document")),
                    "caption": msg.get("caption", ""),
                })

            # Update global offset
            global _last_update_id
            if data.get("result"):
                _last_update_id = max(u["update_id"] for u in data["result"])

            return {"messages": messages, "last_update_id": _last_update_id}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch Telegram history")
        raise HTTPException(502, detail=f"Telegram history failed: {exc}")


@router.post("/send")
async def send_message(req: SendRequest) -> dict[str, Any]:
    """Send a message to the configured Telegram chat."""
    _check_config()

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
                raise HTTPException(502, detail=f"Telegram send failed: {data.get('description', 'Unknown error')}")

            msg = data["result"]
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
