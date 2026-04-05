import os
import sqlite3
import json
from . import storage

class AuditDB:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        storage.ensure_satya_dirs()
        self.db_path = os.path.join(storage.SATYA_DIR, "events", "audit.db")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    signature TEXT NOT NULL
                )
            """)
            conn.commit()

    def append_event(self, event: dict) -> bool:
        """
        Append a signed event to the SQLite database.
        Event is expected to have 'payload' dict and 'signature'.
        """
        payload = event.get("payload", {})
        signature = event.get("signature", "")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_events (
                        timestamp, agent_id, task_id, trace_id, action, details, payload, signature
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    payload.get("timestamp", 0),
                    payload.get("agent_id", ""),
                    payload.get("task_id", ""),
                    payload.get("trace_id", ""),
                    payload.get("action", ""),
                    payload.get("details", ""),
                    json.dumps(payload, sort_keys=True),
                    signature
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Failed to write to audit DB: {e}")
            return False

    def get_all_events(self):
        """
        Returns all events from the DB formatted similarly to the JSONL format.
        """
        if not os.path.exists(self.db_path):
            return []

        events = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT payload, signature FROM audit_events ORDER BY id ASC")
                rows = cursor.fetchall()
                for row in rows:
                    payload_str, signature = row
                    events.append({
                        "payload": json.loads(payload_str),
                        "signature": signature
                    })
        except Exception as e:
            print(f"Failed to read from audit DB: {e}")

        return events
