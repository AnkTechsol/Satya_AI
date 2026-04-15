import os
import hmac
import hashlib
import json
import time
try:
    import fcntl
except ImportError:
    fcntl = None
import sqlite3
from typing import Optional, Dict, Any
from .core import storage

# Simple header/env based auth for agents. ENV:
# SATYA_AGENT_KEYS -> comma separated keys (e.g. key1,key2)
# HUMAN_VIEW_TOKEN -> token for read-only view (optional)
# AUDIT_SECRET -> secret for signing audit events

_AGENT_KEYS = set(k.strip() for k in os.environ.get("SATYA_AGENT_KEYS", "DEMO_KEY").split(",") if k.strip())
_HUMAN_VIEW = os.environ.get("HUMAN_VIEW_TOKEN", "")
_AUDIT_SECRET = os.environ.get("AUDIT_SECRET")


def is_agent_authorized(key: str) -> bool:
    """Check if the provided key is in the allowed agent keys."""
    return key in _AGENT_KEYS

def is_human_authorized(token: str) -> bool:
    """Check if the provided token matches the human view/admin token."""
    return bool(_HUMAN_VIEW and token == _HUMAN_VIEW)

def get_agent_key_from_env() -> str:
    """Helper to get the configured agent key from the environment."""
    return os.environ.get("SATYA_AGENT_KEY", "DEMO_KEY")

def require_agent(key: str):
    """Raise an error if the agent is not authorized."""
    if not is_agent_authorized(key):
        raise PermissionError("Agent credentials required or invalid")

def sign_event(event_data: str, prev_hmac: str = "") -> str:
    """Sign an event payload using HMAC-SHA256, optionally chaining a previous HMAC."""
    if not _AUDIT_SECRET:
        raise ValueError("AUDIT_SECRET environment variable is mandatory for signing audit events.")
    msg = f"{prev_hmac}:{event_data}".encode('utf-8')
    return hmac.new(_AUDIT_SECRET.encode('utf-8'), msg, hashlib.sha256).hexdigest()

def verify_event_chain(events: list[Dict[str, Any]]) -> bool:
    """Verify a chain of signed events."""
    prev_hmac = ""
    for event in events:
        signature = str(event.get("signature") or "")
        payload = event.get("payload", {})
        payload_str = json.dumps(payload, sort_keys=True)

        expected_signature = str(sign_event(payload_str, prev_hmac) or "")
        if not hmac.compare_digest(signature, expected_signature):
            return False
        prev_hmac = signature
    return True

def append_audit_event(agent_id: str, task_id: str, trace_id: str, action: str, details: str, prev_hmac: str = "") -> str:
    """
    Append an atomic, signed audit event to the global events log.
    Fall back to salted atomic file append + rename semantics.
    """
    storage.ensure_satya_dirs()
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    os.makedirs(events_dir, exist_ok=True)

    events_file = os.path.join(events_dir, "audit_log.jsonl")
    tmp_file = events_file + f".{time.time()}.tmp"

    payload = {
        "timestamp": time.time(),
        "agent_id": agent_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "action": action,
        "details": details
    }
    payload_str = json.dumps(payload, sort_keys=True)
    signature = sign_event(payload_str, prev_hmac)

    event = {
        "payload": payload,
        "signature": signature
    }

    # DB initialization
    db_file = os.path.join(events_dir, "audit_log.db")
    db_conn = None
    try:
        db_conn = sqlite3.connect(db_file)
        cursor = db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                agent_id TEXT,
                task_id TEXT,
                trace_id TEXT,
                action TEXT,
                details TEXT,
                signature TEXT,
                payload_json TEXT
            )
        ''')
        db_conn.commit()
    except Exception as e:
        print(f"Failed to initialize SQLite: {e}")
        if db_conn:
            db_conn.close()
            db_conn = None

    # Read the last HMAC if prev_hmac is not provided to maintain the chain
    if not prev_hmac:
        try:
            if db_conn and os.path.exists(db_file):
                cursor = db_conn.cursor()
                cursor.execute("SELECT signature FROM audit_events ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    prev_hmac = row[0]

            if not prev_hmac and os.path.exists(events_file):
                with open(events_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        prev_hmac = last_event.get("signature", "")
            if prev_hmac:
                signature = sign_event(payload_str, prev_hmac)
                event["signature"] = signature
        except Exception as e:
            print(f"Failed to read previous HMAC: {e}")

    event_str = json.dumps(event) + "\n"

    if db_conn:
        try:
            # DB Append
            cursor = db_conn.cursor()
            cursor.execute('''
                INSERT INTO audit_events (timestamp, agent_id, task_id, trace_id, action, details, signature, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (payload["timestamp"], agent_id, task_id, trace_id, action, json.dumps(details) if isinstance(details, dict) else details, signature, json.dumps(payload)))
            db_conn.commit()
        except Exception as e:
            print(f"Failed to write audit event to SQLite, falling back to flat file: {e}")
        finally:
            db_conn.close()

    # Atomic append using fcntl
    try:
        with open(events_file, 'a') as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_EX)
            f.write(event_str)
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_UN)
    except OSError:
        # Fallback if fcntl fails (e.g. Windows or weird FS)
        try:
            with open(tmp_file, 'w') as f_tmp:
                if os.path.exists(events_file):
                    with open(events_file, 'r') as f_in:
                        f_tmp.write(f_in.read())
                f_tmp.write(event_str)
            os.replace(tmp_file, events_file)
        except Exception as e:
            print(f"Failed to write audit event atomically: {e}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            raise

    return signature
