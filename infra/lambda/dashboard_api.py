"""
Lambda handler for ML Lab dashboard API (always-on control plane).

Serves dashboard data from S3 when the GPU EC2 instance is offline.
Returns the same JSON shapes as the Flask dashboard (web_dashboard.py)
so the frontend works identically against either backend.

Also handles Telegram webhook for always-on bot commands (/status,
/sitrep, /help, /start, /stop) even when the EC2 instance is down.

Runtime: Python 3.12, 128MB, 10s timeout
Trigger: API Gateway HTTP API
"""

import base64
import json
import logging
import os
import time
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BUCKET = "ml-lab-004507070771"
PREFIX = "dual-system-research-data/"
CORS_ORIGIN = "https://train.bitbanshee.com"

# Telegram config (from Lambda environment variables)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
FLEET_ID = os.environ.get("FLEET_ID", "fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a")

# Cache TTLs (seconds) — Lambda containers are reused across invocations
_CACHE_TTL_EVAL = 60   # eval metrics change rarely
_CACHE_TTL_FAST = 30   # cost/sitrep may be updated more often

# Static config summary (matches tiny.yaml used for v3 training)
CONFIG_SUMMARY = {
    "model": "gpt2",
    "batch_size": 4,
    "grad_accum": 8,
    "lr": 3e-4,
    "warmup_steps": 2000,
    "max_steps": 50000,
    "checkpoint_every": 1000,
    "eval_every": 1000,
}

# ---------------------------------------------------------------------------
# S3 client & cache
# ---------------------------------------------------------------------------

_s3 = boto3.client("s3")

# Module-level cache: key -> (data, timestamp)
_cache: dict[str, tuple[Any, float]] = {}


def _cache_get(key: str, ttl: float) -> Any | None:
    """Return cached value if still fresh, else None."""
    entry = _cache.get(key)
    if entry is None:
        return None
    data, ts = entry
    if time.time() - ts > ttl:
        return None
    return data


def _cache_set(key: str, data: Any) -> None:
    _cache[key] = (data, time.time())


# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

def _read_s3_json(key: str, ttl: float = _CACHE_TTL_FAST) -> Any | None:
    """Read and parse a JSON file from S3 with caching. Returns None on miss."""
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached

    try:
        resp = _s3.get_object(Bucket=BUCKET, Key=key)
        data = json.loads(resp["Body"].read())
        _cache_set(key, data)
        return data
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise


def _read_s3_text(key: str, ttl: float = _CACHE_TTL_FAST) -> tuple[str | None, str | None]:
    """Read a text file from S3. Returns (content, last_modified_iso) or (None, None)."""
    cache_key = f"text:{key}"
    cached = _cache_get(cache_key, ttl)
    if cached is not None:
        return cached

    try:
        resp = _s3.get_object(Bucket=BUCKET, Key=key)
        content = resp["Body"].read().decode("utf-8")
        modified = resp["LastModified"].isoformat()
        result = (content, modified)
        _cache_set(cache_key, result)
        return result
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None, None
        raise


def _list_eval_keys() -> list[str]:
    """List all eval_step_*.json keys under the eval_metrics/ prefix."""
    cache_key = "_eval_keys"
    cached = _cache_get(cache_key, _CACHE_TTL_EVAL)
    if cached is not None:
        return cached

    prefix = PREFIX + "eval_metrics/"
    keys: list[str] = []
    paginator = _s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                keys.append(obj["Key"])

    _cache_set(cache_key, keys)
    return keys


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def _response(status_code: int, body: Any) -> dict:
    """Build an API Gateway-compatible response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": CORS_ORIGIN,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body, default=str),
    }


def _extract_step_number(key: str) -> int:
    """Extract step number from an eval key like 'eval_step_5000.json'."""
    m = re.search(r"eval_step_(\d+)\.json", key)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

def _handle_status() -> dict:
    """GET /api/status — composite status matching Flask build_status() shape."""
    # Load cost ledger
    ledger = _read_s3_json(PREFIX + "cost/cost_ledger.json")

    # Load all eval files and find the latest by step number
    eval_keys = _list_eval_keys()
    latest_eval = None
    current_step = 0

    if eval_keys:
        # Find the key with highest step number
        best_key = max(eval_keys, key=_extract_step_number)
        latest_eval = _read_s3_json(best_key, ttl=_CACHE_TTL_EVAL)
        if latest_eval:
            current_step = latest_eval.get("step", 0)

    # Extract cost/session data from ledger
    total_cost = 0.0
    sessions = []
    total_training_time_s = 0.0
    total_sessions = 0

    if ledger:
        total_cost = ledger.get("total_cost", 0.0)
        sessions_raw = ledger.get("sessions", [])
        total_sessions = len(sessions_raw)
        now = datetime.now(timezone.utc)

        for sess in sessions_raw:
            boot = sess.get("boot_time")
            end = sess.get("end_time")
            duration_s = None
            if boot:
                try:
                    boot_dt = datetime.fromisoformat(boot)
                    end_dt = datetime.fromisoformat(end) if end else now
                    duration_s = max(0, (end_dt - boot_dt).total_seconds())
                    total_training_time_s += duration_s
                except (ValueError, TypeError):
                    pass
            sessions.append({
                "instance_id": sess.get("instance_id", "?"),
                "instance_type": sess.get("instance_type", "?"),
                "az": sess.get("az", "?"),
                "boot_time": boot,
                "duration_s": duration_s,
                "steps_start": sess.get("steps_start"),
                "steps_end": sess.get("steps_end"),
                "spot_cost": sess.get("spot_cost", 0),
                "finalized": sess.get("finalized", False),
            })

    max_steps = CONFIG_SUMMARY["max_steps"]
    progress_pct = round((current_step / max_steps) * 100, 1) if max_steps else 0.0

    status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_step": current_step,
        "max_steps": max_steps,
        "progress_pct": progress_pct,
        "phase": "offline",
        "eta_seconds": None,
        "elapsed_seconds": None,
        "latest_train": None,
        "latest_eval": latest_eval,
        "next_eval_step": None,
        "gpu": None,
        "infra": None,
        "milestones": [],
        "total_training_time_s": round(total_training_time_s) if total_training_time_s > 0 else None,
        "sessions_breakdown": sessions,
        "instance": {
            "instance_type": None,
            "lifecycle": None,
            "az": None,
            "boot_time_utc": None,
            "uptime_seconds": None,
            "ondemand_price_per_hour": None,
            "ondemand_cost": None,
            "ondemand_projected": None,
            "spot_rate": None,
            "spot_cost": None,
            "spot_projected": None,
            "spot_updated": None,
            "total_run_cost": total_cost,
            "total_sessions": total_sessions,
        },
        "bootstrap": None,
        "log_tail": [],
        "config_summary": CONFIG_SUMMARY,
    }

    return _response(200, status)


def _handle_eval_history() -> dict:
    """GET /api/eval/history — all eval checkpoints sorted by step."""
    eval_keys = _list_eval_keys()
    results: list[dict] = []

    for key in eval_keys:
        data = _read_s3_json(key, ttl=_CACHE_TTL_EVAL)
        if data:
            results.append(data)

    results.sort(key=lambda d: d.get("step", 0))
    return _response(200, results)


def _handle_history() -> dict:
    """GET /api/history — training step history (may not exist)."""
    data = _read_s3_json(PREFIX + "training_history.json")
    return _response(200, data if data is not None else [])


def _handle_sitrep() -> dict:
    """GET /api/sitrep — situation report markdown."""
    content, modified = _read_s3_text(PREFIX + "sitrep.md")
    if content is None:
        return _response(200, {"content": "", "modified": None})
    return _response(200, {"content": content, "modified": modified})


def _handle_cost_total() -> dict:
    """GET /api/cost/total — full cost ledger."""
    data = _read_s3_json(PREFIX + "cost/cost_ledger.json")
    if data is None:
        return _response(200, {})
    return _response(200, data)


def _handle_stream() -> dict:
    """GET /stream — SSE not available offline, return 204."""
    return {
        "statusCode": 204,
        "headers": {
            "Access-Control-Allow-Origin": CORS_ORIGIN,
        },
        "body": "",
    }


def _handle_spot_price() -> dict:
    """POST /api/spot-price — read-only mode, reject writes."""
    return _response(405, {"error": "read-only mode (offline)"})


# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def _send_telegram_reply(chat_id: str, text: str, parse_mode: str = "Markdown") -> None:
    """Send a message via the Telegram Bot API using urllib (no requests dep)."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping reply")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.URLError as e:
        logger.error("Telegram send failed: %s", e)


def _telegram_status(chat_id: str) -> None:
    """Handle /status — build a concise status message from S3 data."""
    ledger = _read_s3_json(PREFIX + "cost/cost_ledger.json")
    eval_keys = _list_eval_keys()

    current_step = 0
    latest_eval = None
    if eval_keys:
        best_key = max(eval_keys, key=_extract_step_number)
        latest_eval = _read_s3_json(best_key, ttl=_CACHE_TTL_EVAL)
        if latest_eval:
            current_step = latest_eval.get("step", 0)

    max_steps = CONFIG_SUMMARY["max_steps"]
    progress_pct = round((current_step / max_steps) * 100, 1) if max_steps else 0.0

    total_cost = ledger.get("total_cost", 0.0) if ledger else 0.0
    total_sessions = len(ledger.get("sessions", [])) if ledger else 0

    lines = [
        "*ML Training Status* (Lambda)",
        f"Step: `{current_step:,}` / `{max_steps:,}` ({progress_pct}%)",
        f"Total cost: `${total_cost:.2f}` over {total_sessions} session(s)",
    ]

    if latest_eval:
        ar = latest_eval.get("ar_loss")
        diff = latest_eval.get("diff_loss")
        ppl = latest_eval.get("perplexity")
        if ar is not None:
            lines.append(f"AR loss: `{ar:.3f}`")
        if diff is not None:
            lines.append(f"Diff loss: `{diff:.3f}`")
        if ppl is not None:
            lines.append(f"Perplexity: `{ppl:.1f}`")

    lines.append(f"\n_Instance: offline (data from S3)_")
    _send_telegram_reply(chat_id, "\n".join(lines))


def _telegram_sitrep(chat_id: str) -> None:
    """Handle /sitrep — send the situation report from S3."""
    content, modified = _read_s3_text(PREFIX + "sitrep.md")
    if not content:
        _send_telegram_reply(chat_id, "_No sitrep available._")
        return

    # Telegram messages max 4096 chars — truncate if needed
    if len(content) > 3800:
        content = content[:3800] + "\n\n_(truncated)_"

    header = f"*Sitrep* (updated {modified or 'unknown'})\n\n"
    _send_telegram_reply(chat_id, header + content)


def _telegram_help(chat_id: str) -> None:
    """Handle /help — list available commands."""
    text = (
        "*Available commands:*\n"
        "/status — Training progress, cost, latest eval\n"
        "/sitrep — Situation report\n"
        "/start — Launch training fleet (set capacity to 1)\n"
        "/stop — Zero training fleet (terminate instance)\n"
        "/help — This message"
    )
    _send_telegram_reply(chat_id, text)


def _telegram_start(chat_id: str) -> None:
    """Handle /start — set fleet target capacity to 1."""
    try:
        ec2 = boto3.client("ec2")
        ec2.modify_fleet(
            FleetId=FLEET_ID,
            TargetCapacitySpecification={
                "TotalTargetCapacity": 1,
                "SpotTargetCapacity": 1,
                "DefaultTargetCapacityType": "spot",
            },
        )
        _send_telegram_reply(chat_id, "Fleet capacity set to 1. Instance launching...")
    except Exception as e:
        logger.error("Fleet start failed: %s", e)
        _send_telegram_reply(chat_id, f"Failed to start fleet: `{e}`")


def _telegram_stop(chat_id: str) -> None:
    """Handle /stop — zero fleet capacity."""
    try:
        ec2 = boto3.client("ec2")
        ec2.modify_fleet(
            FleetId=FLEET_ID,
            TargetCapacitySpecification={
                "TotalTargetCapacity": 0,
                "SpotTargetCapacity": 0,
                "DefaultTargetCapacityType": "spot",
            },
        )
        _send_telegram_reply(chat_id, "Fleet capacity set to 0.")
    except Exception as e:
        logger.error("Fleet stop failed: %s", e)
        _send_telegram_reply(chat_id, f"Failed to stop fleet: `{e}`")


_TELEGRAM_COMMANDS: dict[str, callable] = {
    "/status": _telegram_status,
    "/sitrep": _telegram_sitrep,
    "/help": _telegram_help,
    "/start": _telegram_start,
    "/stop": _telegram_stop,
}


def _handle_telegram_webhook(event: dict) -> dict:
    """POST /api/telegram/webhook — handle incoming Telegram updates."""
    # Validate webhook secret via X-Telegram-Bot-Api-Secret-Token header
    headers = event.get("headers", {})
    secret_token = headers.get("x-telegram-bot-api-secret-token", "")
    if TELEGRAM_WEBHOOK_SECRET and secret_token != TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Telegram webhook secret mismatch")
        return _response(403, {"error": "forbidden"})

    # Parse body (API Gateway may base64-encode it)
    body_raw = event.get("body", "")
    if event.get("isBase64Encoded"):
        body_raw = base64.b64decode(body_raw).decode("utf-8")

    try:
        update = json.loads(body_raw)
    except (json.JSONDecodeError, TypeError):
        return _response(400, {"error": "invalid JSON"})

    # Extract message text and chat_id
    message = update.get("message", {})
    text = (message.get("text") or "").strip()
    chat_id = str(message.get("chat", {}).get("id", ""))

    if not chat_id or not text:
        return _response(200, {"ok": True})

    # Authorize: only respond to our configured chat
    if TELEGRAM_CHAT_ID and chat_id != TELEGRAM_CHAT_ID:
        logger.warning("Telegram message from unauthorized chat: %s", chat_id)
        return _response(200, {"ok": True})

    # Extract command (strip @botname suffix if present)
    command = text.split()[0].split("@")[0].lower()

    handler_fn = _TELEGRAM_COMMANDS.get(command)
    if handler_fn:
        handler_fn(chat_id)
    else:
        _send_telegram_reply(chat_id, f"Unknown command: `{command}`\nTry /help")

    return _response(200, {"ok": True})


# ---------------------------------------------------------------------------
# Route table
# ---------------------------------------------------------------------------

# (method, path) -> handler
_ROUTES: dict[tuple[str, str], callable] = {
    ("GET", "/api/status"):       _handle_status,
    ("GET", "/api/eval/history"): _handle_eval_history,
    ("GET", "/api/history"):      _handle_history,
    ("GET", "/api/sitrep"):       _handle_sitrep,
    ("GET", "/api/cost/total"):   _handle_cost_total,
    ("GET", "/stream"):           _handle_stream,
    ("POST", "/api/spot-price"):  _handle_spot_price,
    # Telegram webhook needs the event for body/headers, handled specially below
}


# ---------------------------------------------------------------------------
# Lambda entry point
# ---------------------------------------------------------------------------

def handler(event: dict, context: Any) -> dict:
    """
    Main Lambda handler for API Gateway HTTP API.

    Event shape (HTTP API v2):
        {"requestContext": {"http": {"method": "GET", "path": "/api/status"}}, ...}
    """
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "GET").upper()
    path = http.get("path", "/")

    # Handle CORS preflight
    if method == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": {
                "Access-Control-Allow-Origin": CORS_ORIGIN,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, X-Telegram-Bot-Api-Secret-Token",
                "Access-Control-Max-Age": "86400",
            },
            "body": "",
        }

    # Telegram webhook — needs full event for body/headers
    if method == "POST" and path == "/api/telegram/webhook":
        return _handle_telegram_webhook(event)

    # Match exact route
    route_handler = _ROUTES.get((method, path))
    if route_handler:
        return route_handler()

    # Fallback: any unmatched /api/* returns 404
    return _response(404, {"error": "not found"})
