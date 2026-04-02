import os
import sqlite3
import json
import time
from typing import Dict, Any, List

from . import storage

def get_db_path() -> str:
    storage.ensure_satya_dirs()
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    os.makedirs(events_dir, exist_ok=True)
    return os.path.join(events_dir, "audit_store.db")

def _get_connection():
    db_path = get_db_path()
    # using isolation_level=None for autocommit
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                signature TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
        """)
    finally:
        conn.close()

def append_event(event: Dict[str, Any], signature: str) -> bool:
    payload = event.get("payload", {})
    init_db()
    conn = _get_connection()
    try:
        conn.execute("""
            INSERT INTO audit_events
            (timestamp, agent_id, task_id, trace_id, action, details, signature, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.get("timestamp", time.time()),
            payload.get("agent_id", ""),
            payload.get("task_id", ""),
            payload.get("trace_id", ""),
            payload.get("action", ""),
            payload.get("details", ""),
            signature,
            json.dumps(payload)
        ))
        return True
    except Exception as e:
        print(f"Failed to append to SQLite audit store: {e}")
        raise e
    finally:
        conn.close()

def get_last_signature() -> str:
    init_db()
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT signature FROM audit_events ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""
    finally:
        conn.close()

def get_all_events() -> List[Dict[str, Any]]:
    init_db()
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT payload_json, signature FROM audit_events ORDER BY id ASC")
        events = []
        for row in cursor:
            payload_json, signature = row
            events.append({
                "payload": json.loads(payload_json),
                "signature": signature
            })
        return events
    finally:
        conn.close()
