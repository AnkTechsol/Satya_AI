import sqlite3
import os
import json
import logging
from typing import List, Dict, Any, Tuple
from . import storage

logger = logging.getLogger(__name__)

class AuditDB:
    def __init__(self):
        storage.ensure_satya_dirs()
        self.db_path = os.path.join(storage.SATYA_DIR, "events", "audit.db")
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
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

    def append_event(self, event: Dict[str, Any], signature: str) -> bool:
        """Append a signed event to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()

            payload = event.get("payload", {})
            cursor.execute('''
                INSERT INTO audit_events (timestamp, agent_id, task_id, trace_id, action, details, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                payload.get("timestamp"),
                payload.get("agent_id"),
                payload.get("task_id"),
                payload.get("trace_id"),
                payload.get("action"),
                payload.get("details"),
                signature
            ))

            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to append to audit db: {e}")
            return False

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Retrieve all events from the database for verification."""
        events = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp, agent_id, task_id, trace_id, action, details, signature FROM audit_events ORDER BY id ASC')
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                events.append({
                    "payload": {
                        "timestamp": row[0],
                        "agent_id": row[1],
                        "task_id": row[2],
                        "trace_id": row[3],
                        "action": row[4],
                        "details": row[5]
                    },
                    "signature": row[6]
                })
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve events from audit db: {e}")
        return events

    def get_last_signature(self) -> str:
        """Retrieve the signature of the last event appended."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT signature FROM audit_events ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            conn.close()

            if row:
                return row[0]
        except sqlite3.Error as e:
            logger.error(f"Failed to get last signature from audit db: {e}")
        return ""
