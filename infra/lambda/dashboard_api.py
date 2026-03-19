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
_TRAINING_RUN_DEFAULT = "v4"

# Control plane config (for elevation commands via Cloudflare tunnel)
CONTROL_PLANE_URL = os.environ.get("CONTROL_PLANE_URL", "https://lab.bitbanshee.com")
TG_ELEV_SECRET = os.environ.get("TELEGRAM_ELEVATION_SECRET", "")
CF_SERVICE_ID = os.environ.get("CF_SERVICE_TOKEN_ID", "")
CF_SERVICE_SECRET = os.environ.get("CF_SERVICE_TOKEN_SECRET", "")

# Cache TTLs (seconds) — Lambda containers are reused across invocations
_CACHE_TTL_EVAL = 60   # eval metrics change rarely
_CACHE_TTL_FAST = 30   # cost/sitrep may be updated more often
_CACHE_TTL_RUN = 120   # current_run.json changes only at run start

# Fallback config summary (used if current_run.json is missing from S3)
_CONFIG_SUMMARY_DEFAULT = {
    "model": "gpt2",
    "batch_size": 4,
    "grad_accum": 8,
    "lr": 3e-4,
    "warmup_steps": 2000,
    "max_steps": 75000,
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


def _get_current_run() -> dict:
    """Read current_run.json from S3. Returns {"run": str, "max_steps": int, "config": dict}."""
    cached = _cache_get("_current_run", _CACHE_TTL_RUN)
    if cached is not None:
        return cached

    data = _read_s3_json(PREFIX + "current_run.json", ttl=_CACHE_TTL_RUN)
    if data and "run" in data:
        result = {
            "run": data["run"],
            "max_steps": data.get("max_steps", _CONFIG_SUMMARY_DEFAULT["max_steps"]),
            "config": {**_CONFIG_SUMMARY_DEFAULT, **{k: v for k, v in data.items() if k in _CONFIG_SUMMARY_DEFAULT}},
        }
    else:
        result = {
            "run": _TRAINING_RUN_DEFAULT,
            "max_steps": _CONFIG_SUMMARY_DEFAULT["max_steps"],
            "config": _CONFIG_SUMMARY_DEFAULT,
        }
    _cache_set("_current_run", result)
    return result


def _list_eval_keys() -> list[str]:
    """List all eval_step_*.json keys under the eval_metrics/ prefix."""
    cache_key = "_eval_keys"
    cached = _cache_get(cache_key, _CACHE_TTL_EVAL)
    if cached is not None:
        return cached

    run = _get_current_run()
    prefix = PREFIX + f"eval_metrics/{run['run']}/"
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

    run_info = _get_current_run()
    max_steps = run_info["max_steps"]
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
        "config_summary": run_info["config"],
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

# Collects bot replies during a single webhook invocation for CP forwarding
_reply_collector: list[dict] = []


def _send_telegram_reply(chat_id: str, text: str, parse_mode: str = "Markdown",
                         reply_markup: dict | None = None) -> dict | None:
    """Send a message via the Telegram Bot API. Returns message data or None."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping reply")
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        body["reply_markup"] = reply_markup
    payload = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        if data.get("ok"):
            result = data["result"]
            _reply_collector.append(_msg_to_stored(result, "Bitbanshee", True))
            return result
    except urllib.error.URLError as e:
        logger.error("Telegram send failed: %s", e)
    return None


def _answer_callback_query(callback_id: str, text: str = "") -> None:
    """Acknowledge a callback query (removes loading spinner on button)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = json.dumps({"callback_query_id": callback_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.URLError as e:
        logger.error("answerCallbackQuery failed: %s", e)


def _edit_telegram_message(chat_id: str, message_id: int, text: str,
                           parse_mode: str = "Markdown") -> None:
    """Edit an existing message (removes buttons after action)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.URLError as e:
        logger.error("editMessageText failed: %s", e)


def _call_control_plane(method: str, path: str, body: dict | None = None, timeout: int = 8) -> dict | None:
    """Call control plane API via Cloudflare tunnel. Returns JSON or None."""
    url = f"{CONTROL_PLANE_URL}{path}"
    headers = {"X-Telegram-Secret": TG_ELEV_SECRET, "Content-Type": "application/json", "User-Agent": "BitLabLambda/1.0"}
    if CF_SERVICE_ID:
        headers["CF-Access-Client-Id"] = CF_SERVICE_ID
        headers["CF-Access-Client-Secret"] = CF_SERVICE_SECRET
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())
    except Exception as e:
        logger.error("Control plane call failed: %s %s -> %s", method, path, e)
        if hasattr(e, 'read'):
            logger.error("Response body: %s", e.read()[:500])
        return None


def _forward_to_cp(messages: list[dict]) -> None:
    """Forward messages to the control plane for dashboard mirroring."""
    if not messages:
        return
    try:
        _call_control_plane("POST", "/api/telegram/ingest", body={"messages": messages}, timeout=5)
    except Exception as e:
        logger.warning("CP ingest failed: %s", e)


def _msg_to_stored(msg: dict, from_name: str, is_bot: bool) -> dict:
    """Convert a Telegram API message result to our stored format."""
    return {
        "id": msg.get("message_id", int(time.time() * 1000)),
        "from": from_name,
        "is_bot": is_bot,
        "text": msg.get("text", ""),
        "date": msg.get("date", int(time.time())),
        "has_photo": False,
        "has_document": False,
        "caption": "",
    }


def _telegram_status(chat_id: str, args: list[str]) -> None:
    """Handle /status [ml|cp] — dispatch to subcommand or combined view."""
    if args and args[0].lower() == "ml":
        _telegram_status_ml(chat_id)
    elif args and args[0].lower() == "cp":
        _telegram_status_cp(chat_id)
    else:
        # Combined: ML summary + CP health
        _telegram_status_ml(chat_id)
        _telegram_status_cp(chat_id)


def _telegram_status_cp(chat_id: str) -> None:
    """Handle /status cp — control plane health + elevation summary."""
    health = _call_control_plane("GET", "/health")
    elev = _call_control_plane("GET", "/api/tg-elev/summary")

    if not health:
        _send_telegram_reply(chat_id, "*Control Plane*\n_Unreachable_")
        return

    lines = [
        "*Control Plane*",
        f"Status: `{health.get('status', '?')}`",
        f"Uptime: `{round(health.get('uptime', 0) / 3600, 1)}h`",
    ]

    if elev:
        pending = elev.get("pending", [])
        active = elev.get("active")
        if pending:
            lines.append(f"\nPending elevations: {len(pending)}")
            for p in pending[:3]:
                short_id = p["id"][:8]
                lines.append(f"  `{short_id}` — {p.get('action', '?')}")
        if active:
            lines.append(f"\nActive elevation: `{active['id'][:8]}`")
            lines.append(f"  Action: {active.get('action', '?')}")
            lines.append(f"  Expires: {active.get('expires_at', '?')}")
        if not pending and not active:
            lines.append("\nNo pending or active elevations")

    _send_telegram_reply(chat_id, "\n".join(lines))


def _telegram_status_ml(chat_id: str) -> None:
    """Handle /status ml — ML training detail from S3 data."""
    ledger = _read_s3_json(PREFIX + "cost/cost_ledger.json")
    eval_keys = _list_eval_keys()

    current_step = 0
    latest_eval = None
    if eval_keys:
        best_key = max(eval_keys, key=_extract_step_number)
        latest_eval = _read_s3_json(best_key, ttl=_CACHE_TTL_EVAL)
        if latest_eval:
            current_step = latest_eval.get("step", 0)

    run_info = _get_current_run()
    max_steps = run_info["max_steps"]
    progress_pct = round((current_step / max_steps) * 100, 1) if max_steps else 0.0

    total_cost = ledger.get("total_cost", 0.0) if ledger else 0.0
    total_sessions = len(ledger.get("sessions", [])) if ledger else 0

    lines = [
        f"*ML Training — {run_info['run']}*",
        f"Step: `{current_step:,}` / `{max_steps:,}` ({progress_pct}%)",
        f"Cost: `${total_cost:.2f}` ({total_sessions} sessions)",
    ]

    if latest_eval:
        ar_ppl = latest_eval.get("ar_perplexity")
        diff = latest_eval.get("diff_loss")
        s1_acc = latest_eval.get("s1_token_accuracy")
        auroc = latest_eval.get("conf_auroc")
        ece = latest_eval.get("conf_ece")
        if ar_ppl is not None:
            lines.append(f"AR PPL: `{ar_ppl:.2f}`")
        if diff is not None:
            lines.append(f"Diff loss: `{diff:.3f}`")
        if s1_acc is not None:
            lines.append(f"S1 accuracy: `{s1_acc*100:.1f}%`")
        if auroc is not None:
            lines.append(f"AUROC: `{auroc:.3f}`")
        if ece is not None:
            lines.append(f"ECE: `{ece:.4f}`")

    lines.append(f"\n_Source: S3 (Lambda)_")
    _send_telegram_reply(chat_id, "\n".join(lines))


def _telegram_sitrep(chat_id: str, args: list[str]) -> None:
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


def _telegram_gpu(chat_id: str, args: list[str]) -> None:
    """Handle /gpu — fleet detail with instance info."""
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        fleet = ec2.describe_fleets(FleetIds=[FLEET_ID])["Fleets"][0]
        state = fleet.get("FleetState", "unknown")
        target = fleet.get("TargetCapacitySpecification", {}).get("TotalTargetCapacity", 0)
        fulfilled = fleet.get("FulfilledCapacity", 0)

        lines = [
            "*GPU Fleet Detail*\n",
            f"State: `{state}`",
            f"Capacity: {int(fulfilled)}/{target}",
        ]

        # Get active instances
        instances = ec2.describe_fleet_instances(FleetId=FLEET_ID).get("ActiveInstances", [])
        if instances:
            instance_ids = [i["InstanceId"] for i in instances]
            reservations = ec2.describe_instances(InstanceIds=instance_ids)["Reservations"]
            for res in reservations:
                for inst in res["Instances"]:
                    iid = inst["InstanceId"]
                    itype = inst["InstanceType"]
                    istate = inst["State"]["Name"]
                    az = inst["Placement"]["AvailabilityZone"]
                    ip = inst.get("PublicIpAddress", "none")
                    launch = inst.get("LaunchTime", "")
                    lines.append(f"\n*Instance*")
                    lines.append(f"ID: `{iid}`")
                    lines.append(f"Type: `{itype}` | State: {istate}")
                    lines.append(f"AZ: {az} | IP: {ip}")
                    if launch:
                        lines.append(f"Launched: {launch}")
        else:
            lines.append("\nNo active instances")

        _send_telegram_reply(chat_id, "\n".join(lines))
    except Exception as e:
        logger.error("GPU detail failed: %s", e)
        _send_telegram_reply(chat_id, f"GPU detail failed: `{e}`")


def _telegram_cost(chat_id: str, args: list[str]) -> None:
    """Handle /cost — month-to-date AWS spend from Cost Explorer."""
    try:
        ce = boto3.client("ce", region_name="us-east-1")
        now = datetime.now(timezone.utc)
        start = now.strftime("%Y-%m-01")
        end = now.strftime("%Y-%m-%d")

        result = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
        )

        total = 0.0
        for r in result.get("ResultsByTime", []):
            total += float(r["Total"]["UnblendedCost"]["Amount"])

        # Also include training cost from ledger
        ledger = _read_s3_json(PREFIX + "cost/cost_ledger.json")
        training_cost = ledger.get("total_cost", 0.0) if ledger else 0.0

        lines = [
            "*Cost Summary*\n",
            f"MTD AWS spend: *${total:.2f}*",
            f"Training spot cost: *${training_cost:.2f}*",
        ]
        _send_telegram_reply(chat_id, "\n".join(lines))
    except Exception as e:
        logger.error("Cost check failed: %s", e)
        _send_telegram_reply(chat_id, f"Cost check failed: `{e}`")


def _telegram_help(chat_id: str, args: list[str]) -> None:
    """Handle /help — list available commands."""
    text = (
        "*Bit — Lab Commands*\n\n"
        "*Status*\n"
        "/status — Overview of all projects\n"
        "/status ml — ML training detail\n"
        "/status cp — Control plane health\n\n"
        "*ML Training*\n"
        "/gpu — GPU fleet instances\n"
        "/cost — Month-to-date AWS spend\n"
        "/sitrep — Situation report\n"
        "/start — Launch training fleet\n"
        "/stop — Stop training fleet\n\n"
        "*Elevation*\n"
        "/elev — Current elevation status\n"
        "/elev approve <id> — Approve pending request\n"
        "/elev deny <id> — Deny pending request\n"
        "/elev revoke — Revoke active elevation\n"
        "/elev history — Recent elevation log\n\n"
        "*Tasks*\n"
        "/task — List open tasks\n"
        "/task <text> — Create a task\n"
        "/task high <text> — Create with priority\n"
        "/task done <id> — Mark task done\n"
        "/task delete <id> — Delete a task\n\n"
        "*Peer Review*\n"
        "/skip — Check pending skip request\n"
        "/skip approve — Approve Bit's skip\n"
        "/skip deny — Deny (require full review)\n\n"
        "/help — This message"
    )
    _send_telegram_reply(chat_id, text)


def _telegram_start(chat_id: str, args: list[str]) -> None:
    """Handle /start — set fleet target capacity to 1."""
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        ec2.modify_fleet(
            FleetId=FLEET_ID,
            TargetCapacitySpecification={
                "TotalTargetCapacity": 1,
            },
        )
        _send_telegram_reply(chat_id, "Fleet capacity set to 1. Instance launching...")
    except Exception as e:
        logger.error("Fleet start failed: %s", e)
        _send_telegram_reply(chat_id, f"Failed to start fleet: `{e}`")


def _telegram_stop(chat_id: str, args: list[str]) -> None:
    """Handle /stop — zero fleet capacity."""
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        ec2.modify_fleet(
            FleetId=FLEET_ID,
            TargetCapacitySpecification={
                "TotalTargetCapacity": 0,
            },
        )
        _send_telegram_reply(chat_id, "Fleet capacity set to 0.")
    except Exception as e:
        logger.error("Fleet stop failed: %s", e)
        _send_telegram_reply(chat_id, f"Failed to stop fleet: `{e}`")


def _telegram_elev(chat_id: str, args: list[str]) -> None:
    """Handle /elev [approve|deny|revoke|history] — elevation commands via control plane."""
    if not args:
        # Show current elevation state
        data = _call_control_plane("GET", "/api/tg-elev/summary")
        if not data:
            _send_telegram_reply(chat_id, "_Control plane unreachable_")
            return
        pending = data.get("pending", [])
        active = data.get("active")
        lines = ["*Elevation Status*"]
        if pending:
            lines.append(f"\n*Pending* ({len(pending)}):")
            for p in pending:
                short_id = p["id"][:8]
                lines.append(f"  `{short_id}` — {p.get('action', '?')}")
                lines.append(f"    _{p.get('justification', '')}_")
        if active:
            lines.append(f"\n*Active*: `{active['id'][:8]}`")
            lines.append(f"  Action: {active.get('action', '?')}")
            lines.append(f"  Expires: {active.get('expires_at', '?')}")
        if not pending and not active:
            lines.append("\nNo pending or active elevations")
        _send_telegram_reply(chat_id, "\n".join(lines))
        return

    subcmd = args[0].lower()

    if subcmd == "approve" and len(args) >= 2:
        result = _call_control_plane("POST", f"/api/tg-elev/approve/{args[1]}")
        if result:
            _send_telegram_reply(chat_id, f"Approved elevation `{result.get('id', args[1])[:8]}`")
        else:
            _send_telegram_reply(chat_id, f"Failed to approve `{args[1]}` — check ID prefix or control plane status")

    elif subcmd == "deny" and len(args) >= 2:
        result = _call_control_plane("POST", f"/api/tg-elev/deny/{args[1]}")
        if result:
            _send_telegram_reply(chat_id, f"Denied elevation `{result.get('id', args[1])[:8]}`")
        else:
            _send_telegram_reply(chat_id, f"Failed to deny `{args[1]}` — check ID prefix or control plane status")

    elif subcmd == "revoke":
        result = _call_control_plane("POST", "/api/tg-elev/revoke")
        if result:
            _send_telegram_reply(chat_id, f"Revoked elevation `{result.get('id', '?')[:8]}`")
        else:
            _send_telegram_reply(chat_id, "Failed to revoke — no active elevation or control plane unreachable")

    elif subcmd == "history":
        data = _call_control_plane("GET", "/api/tg-elev/history")
        if not data:
            _send_telegram_reply(chat_id, "_Control plane unreachable_")
            return
        if not data:
            _send_telegram_reply(chat_id, "_No elevation history_")
            return
        lines = ["*Elevation History*"]
        for entry in data[:10]:
            short_id = entry["id"][:8]
            status = entry.get("status", "?")
            action = entry.get("action", "?")
            when = entry.get("requested_at", "?")[:16]
            lines.append(f"`{short_id}` {status} — {action} ({when})")
        _send_telegram_reply(chat_id, "\n".join(lines))

    else:
        _send_telegram_reply(chat_id, "Usage: /elev [approve <id> | deny <id> | revoke | history]")


def _telegram_skip(chat_id: str, args: list[str]) -> None:
    """Handle /skip [approve|deny] — Byte peer review skip approval."""
    if not args:
        pending = _call_control_plane("GET", "/api/byte-review/pending")
        if not pending or not pending.get("pending"):
            _send_telegram_reply(chat_id, "_No pending skip request_")
        else:
            reason = pending.get("reason", "no reason given")
            status = pending.get("status", "pending")
            _send_telegram_reply(chat_id, f"*Byte Review Skip*\nStatus: `{status}`\nReason: {reason}")
        return

    subcmd = args[0].lower()
    if subcmd == "approve":
        result = _call_control_plane("POST", "/api/byte-review/approve")
        if result and result.get("success"):
            _send_telegram_reply(chat_id, "Byte review skip *approved*")
        else:
            _send_telegram_reply(chat_id, "Failed — no pending skip or control plane unreachable")
    elif subcmd == "deny":
        result = _call_control_plane("POST", "/api/byte-review/deny")
        if result and result.get("success"):
            _send_telegram_reply(chat_id, "Byte review skip *denied* — Bit must do full review")
        else:
            _send_telegram_reply(chat_id, "Failed — no pending skip or control plane unreachable")
    else:
        _send_telegram_reply(chat_id, "Usage: /skip [approve | deny]")


def _telegram_task(chat_id: str, args: list[str]) -> None:
    """Handle /task — create and manage tasks from Telegram.

    /task                       — list open tasks
    /task <text>                — create a new task (med priority)
    /task high <text>           — create with explicit priority
    /task done <id>             — mark a task done
    /task delete <id>           — delete a task
    """
    if not args:
        # List open tasks
        data = _call_control_plane("GET", "/api/tasks/list")
        if not data:
            _send_telegram_reply(chat_id, "_Control plane unreachable_")
            return
        tasks = [t for t in data.get("tasks", []) if not t.get("done")]
        if not tasks:
            _send_telegram_reply(chat_id, "_No open tasks_")
            return
        lines = [f"*Tasks* ({len(tasks)} open)"]
        for t in tasks[:15]:
            pri = {"high": "🔴", "med": "🟡", "low": "⚪"}.get(t.get("priority", "low"), "⚪")
            short_id = t["id"][:8]
            prefix = t.get("text", "")[:60]
            approved = "" if t.get("approved") else " ⏳"
            lines.append(f"{pri} `{short_id}` {prefix}{approved}")
        _send_telegram_reply(chat_id, "\n".join(lines))
        return

    subcmd = args[0].lower()

    # /task done <id_prefix>
    if subcmd == "done" and len(args) >= 2:
        id_prefix = args[1].lower()
        # Resolve full task ID from prefix
        data = _call_control_plane("GET", "/api/tasks/list")
        if not data:
            _send_telegram_reply(chat_id, "_Control plane unreachable_")
            return
        match = next((t for t in data.get("tasks", []) if t["id"].lower().startswith(id_prefix)), None)
        if not match:
            _send_telegram_reply(chat_id, f"No task matching `{id_prefix}`")
            return
        result = _call_control_plane("PUT", f"/api/tasks/{match['id']}", {"done": True})
        if result and result.get("success"):
            _send_telegram_reply(chat_id, f"✓ Marked done: {match['text'][:50]}")
        else:
            _send_telegram_reply(chat_id, "Failed to update task")
        return

    # /task delete <id_prefix>
    if subcmd == "delete" and len(args) >= 2:
        id_prefix = args[1].lower()
        data = _call_control_plane("GET", "/api/tasks/list")
        if not data:
            _send_telegram_reply(chat_id, "_Control plane unreachable_")
            return
        match = next((t for t in data.get("tasks", []) if t["id"].lower().startswith(id_prefix)), None)
        if not match:
            _send_telegram_reply(chat_id, f"No task matching `{id_prefix}`")
            return
        result = _call_control_plane("DELETE", f"/api/tasks/{match['id']}")
        if result and result.get("success"):
            _send_telegram_reply(chat_id, f"🗑 Deleted: {match['text'][:50]}")
        else:
            _send_telegram_reply(chat_id, "Failed to delete task")
        return

    # /task [high|med|low] <text> — create a task
    priority = "med"
    text_parts = args
    if subcmd in ("high", "med", "low") and len(args) >= 2:
        priority = subcmd
        text_parts = args[1:]
    task_text = " ".join(text_parts)

    result = _call_control_plane("POST", "/api/tasks/create", {
        "text": task_text,
        "priority": priority,
        "author": "Bitbanshee",
    })
    if result and result.get("success"):
        task = result["task"]
        _send_telegram_reply(chat_id, f"✅ Created `{task['id'][:8]}`: {task_text[:50]}")
    else:
        _send_telegram_reply(chat_id, "Failed to create task")


_TELEGRAM_COMMANDS: dict[str, callable] = {
    "/status": _telegram_status,
    "/gpu": _telegram_gpu,
    "/cost": _telegram_cost,
    "/sitrep": _telegram_sitrep,
    "/help": _telegram_help,
    "/start": _telegram_start,
    "/stop": _telegram_stop,
    "/elev": _telegram_elev,
    "/skip": _telegram_skip,
    "/task": _telegram_task,
}


def _handle_callback_query(callback: dict) -> dict:
    """Handle inline keyboard button taps.

    callback_data format:
      - "skip_approve" / "skip_deny"
      - "elev_approve_{id_prefix}" / "elev_deny_{id_prefix}"
      - "elev_revoke"
    """
    cb_id = callback.get("id", "")
    cb_data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    message_id = message.get("message_id")
    original_text = message.get("text", "")

    # Authorize
    if TELEGRAM_CHAT_ID and chat_id != TELEGRAM_CHAT_ID:
        _answer_callback_query(cb_id, "Unauthorized")
        return _response(200, {"ok": True})

    if cb_data == "skip_approve":
        result = _call_control_plane("POST", "/api/byte-review/approve")
        if result and result.get("success"):
            _answer_callback_query(cb_id, "Skip approved")
            _edit_telegram_message(chat_id, message_id,
                                   original_text + "\n\n*Approved*")
        else:
            _answer_callback_query(cb_id, "Failed")

    elif cb_data == "skip_deny":
        result = _call_control_plane("POST", "/api/byte-review/deny")
        if result and result.get("success"):
            _answer_callback_query(cb_id, "Skip denied")
            _edit_telegram_message(chat_id, message_id,
                                   original_text + "\n\n*Denied* — full review required")
        else:
            _answer_callback_query(cb_id, "Failed")

    elif cb_data.startswith("elev_approve_"):
        id_prefix = cb_data[len("elev_approve_"):]
        result = _call_control_plane("POST", f"/api/tg-elev/approve/{id_prefix}")
        if result:
            _answer_callback_query(cb_id, "Elevation approved")
            _edit_telegram_message(chat_id, message_id,
                                   original_text + f"\n\n*Approved* `{id_prefix}`")
        else:
            _answer_callback_query(cb_id, "Failed")

    elif cb_data.startswith("elev_deny_"):
        id_prefix = cb_data[len("elev_deny_"):]
        result = _call_control_plane("POST", f"/api/tg-elev/deny/{id_prefix}")
        if result:
            _answer_callback_query(cb_id, "Elevation denied")
            _edit_telegram_message(chat_id, message_id,
                                   original_text + f"\n\n*Denied* `{id_prefix}`")
        else:
            _answer_callback_query(cb_id, "Failed")

    elif cb_data == "elev_revoke":
        result = _call_control_plane("POST", "/api/tg-elev/revoke")
        if result:
            _answer_callback_query(cb_id, "Elevation revoked")
            _edit_telegram_message(chat_id, message_id,
                                   original_text + "\n\n*Revoked*")
        else:
            _answer_callback_query(cb_id, "Failed")

    else:
        _answer_callback_query(cb_id, "Unknown action")

    # Forward the action to CP for dashboard mirroring
    action_stored = {
        "id": int(time.time() * 1000),
        "from": callback.get("from", {}).get("first_name", "Unknown"),
        "is_bot": False,
        "text": f"[button] {cb_data}",
        "date": int(time.time()),
        "has_photo": False,
        "has_document": False,
        "caption": "",
    }
    _forward_to_cp([action_stored])

    return _response(200, {"ok": True})


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

    # Handle inline keyboard button taps (callback_query)
    callback = update.get("callback_query")
    if callback:
        return _handle_callback_query(callback)

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

    # Build incoming message for CP forwarding
    from_user = message.get("from", {})
    from_name = from_user.get("first_name", "Unknown")
    incoming_stored = {
        "id": message.get("message_id", int(time.time() * 1000)),
        "from": from_name,
        "is_bot": False,
        "text": text,
        "date": message.get("date", int(time.time())),
        "has_photo": False,
        "has_document": False,
        "caption": "",
    }

    # Clear reply collector for this invocation
    _reply_collector.clear()

    # Parse command and arguments
    parts = text.strip().split()
    command = parts[0].split("@")[0].lower()
    args = parts[1:]

    handler_fn = _TELEGRAM_COMMANDS.get(command)
    if handler_fn:
        handler_fn(chat_id, args)
    else:
        _send_telegram_reply(chat_id, f"Unknown command: `{command}`\nTry /help")

    # Forward incoming message + all bot replies to CP
    all_messages = [incoming_stored] + list(_reply_collector)
    _forward_to_cp(all_messages)

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
