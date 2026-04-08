import os
import hmac
import hashlib
import json
import time
import fcntl
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
        signature = event.get("signature")
        payload = event.get("payload", {})
        payload_str = json.dumps(payload, sort_keys=True)

        expected_signature = sign_event(payload_str, prev_hmac)
        if not hmac.compare_digest(str(signature or ""), expected_signature):
            return False
        prev_hmac = signature
    return True

def append_audit_event(agent_id: str, task_id: str, trace_id: str, action: str, details: str, prev_hmac: str = "") -> str:
    """
    Append an atomic, signed audit event to the global events log.
    If SATYA_USE_AUDIT_DB=1, use an append-only SQLite DB.
    Otherwise, fall back to salted atomic file append + rename semantics.
    """
    storage.ensure_satya_dirs()
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    os.makedirs(events_dir, exist_ok=True)

    use_db = os.environ.get("SATYA_USE_AUDIT_DB") == "1"

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

    if use_db:
        db_file = os.path.join(events_dir, "audit_log.db")
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature TEXT NOT NULL,
                payload TEXT NOT NULL
            )
        ''')

        # Read last HMAC to maintain chain
        if not prev_hmac:
            cur.execute('SELECT signature FROM audit_events ORDER BY id DESC LIMIT 1')
            row = cur.fetchone()
            if row:
                prev_hmac = row[0]
                signature = sign_event(payload_str, prev_hmac)
                event["signature"] = signature
            else:
                # Fallback to jsonl if DB is empty - migrate them
                events_file = os.path.join(events_dir, "audit_log.jsonl")
                if os.path.exists(events_file):
                    try:
                        with open(events_file, 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                old_event = json.loads(line)
                                cur.execute('INSERT INTO audit_events (signature, payload) VALUES (?, ?)',
                                            (old_event["signature"], json.dumps(old_event["payload"])))
                            conn.commit()
                            if lines:
                                last_event = json.loads(lines[-1])
                                prev_hmac = last_event.get("signature", "")
                                signature = sign_event(payload_str, prev_hmac)
                                event["signature"] = signature
                    except Exception as e:
                        pass
        try:
            cur.execute('INSERT INTO audit_events (signature, payload) VALUES (?, ?)', (event["signature"], json.dumps(payload)))
            conn.commit()
        except Exception as e:
            print(f"Failed to insert audit event into DB: {e}")
            raise
        finally:
            conn.close()
        return event["signature"]
    else:
        events_file = os.path.join(events_dir, "audit_log.jsonl")
        tmp_file = events_file + f".{time.time()}.tmp"

        # Read the last HMAC if prev_hmac is not provided to maintain the chain
        if not prev_hmac and os.path.exists(events_file):
            try:
                with open(events_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        prev_hmac = last_event.get("signature", "")
                        signature = sign_event(payload_str, prev_hmac)
                        event["signature"] = signature
            except Exception as e:
                print(f"Failed to read previous HMAC: {e}")

        event_str = json.dumps(event) + "\n"

        # Atomic append using fcntl
        try:
            with open(events_file, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(event_str)
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
