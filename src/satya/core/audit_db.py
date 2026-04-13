import sqlite3
import os
import json
import logging
from typing import Dict, Any

from . import storage

logger = logging.getLogger(__name__)

def get_db_path():
    storage.ensure_satya_dirs()
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    os.makedirs(events_dir, exist_ok=True)
    return os.path.join(events_dir, "audit.db")

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            agent_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            trace_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            signature TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_event(payload: Dict[str, Any], signature: str):
    init_db()
    db_path = get_db_path()
    try:
        details_val = payload.get("details", "")
        if isinstance(details_val, dict):
            details_val = json.dumps(details_val)
        elif not isinstance(details_val, str):
            details_val = str(details_val)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_log (timestamp, agent_id, task_id, trace_id, action, details, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            payload.get("timestamp", 0.0),
            payload.get("agent_id", ""),
            payload.get("task_id", ""),
            payload.get("trace_id", ""),
            payload.get("action", ""),
            details_val,
            signature
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to insert audit event into sqlite: {e}")
