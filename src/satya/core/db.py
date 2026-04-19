import os
import sqlite3
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

_DB_INITIALIZED = False

def get_db_path() -> str:
    """Return the path to the SQLite DB if configured, else empty string."""
    return os.environ.get("SATYA_SQLITE_DB", "")

def init_db():
    """Initialize the SQLite DB schema if it doesn't exist."""
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return

    db_path = get_db_path()
    if not db_path:
        return

    try:
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
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
        _DB_INITIALIZED = True
    except Exception as e:
        logger.error(f"Failed to initialize SQLite DB: {e}")

def append_event_to_db(event: Dict[str, Any]):
    """Append a signed audit event to the SQLite database."""
    db_path = get_db_path()
    if not db_path:
        return

    init_db()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        payload = event.get("payload", {})

        # Serialize details to string to prevent interface errors
        details = payload.get("details", "")
        if isinstance(details, dict):
            details = json.dumps(details)
        elif not isinstance(details, str):
            details = str(details)

        cursor.execute('''
            INSERT INTO audit_log (timestamp, agent_id, task_id, trace_id, action, details, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            payload.get("timestamp", 0.0),
            str(payload.get("agent_id", "")),
            str(payload.get("task_id", "")),
            str(payload.get("trace_id", "")),
            str(payload.get("action", "")),
            details,
            str(event.get("signature", ""))
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to append event to SQLite DB: {e}")
