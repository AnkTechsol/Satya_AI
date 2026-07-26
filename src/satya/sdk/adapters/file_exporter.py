import json
import csv
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class JSONLAdapter(ExportAdapter):
    """Exports traces and logs to a JSONL file."""
    def __init__(self, filepath: str = "satya_data/traces.jsonl"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = data.copy()
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": payload
        }
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

class CSVAdapter(ExportAdapter):
    """Exports traces to a CSV file."""
    def __init__(self, filepath: str = "satya_data/traces.csv"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        self._ensure_header()

    def _ensure_header(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = data.copy()
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                trace_id,
                agent_name,
                event_type,
                json.dumps(payload)
            ])

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
