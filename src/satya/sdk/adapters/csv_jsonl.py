import os
import json
import csv
from datetime import datetime, timezone
from .base import ExportAdapter

class CSVJSONLAdapter(ExportAdapter):
    """
    CSV/JSONL Adapter.
    Exports traces and logs to CSV and JSONL files for local offline analysis.
    """
    def __init__(self, export_dir: str):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.traces_csv = os.path.join(self.export_dir, "traces.csv")
        self.traces_jsonl = os.path.join(self.export_dir, "traces.jsonl")
        self.logs_csv = os.path.join(self.export_dir, "logs.csv")
        self.logs_jsonl = os.path.join(self.export_dir, "logs.jsonl")

    def _append_jsonl(self, filepath: str, data: dict):
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def _append_csv(self, filepath: str, data: dict, fieldnames: list):
        file_exists = os.path.exists(filepath)
        with open(filepath, "a", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        payload_data = data.copy()
        record = {
            "timestamp": now,
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": json.dumps(payload_data)
        }
        self._append_jsonl(self.traces_jsonl, record)
        self._append_csv(self.traces_csv, record, ["timestamp", "trace_id", "agent_name", "event_type", "data"])

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "timestamp": now,
            "agent_name": agent_name,
            "task_id": task_id or "",
            "message": message
        }
        self._append_jsonl(self.logs_jsonl, record)
        self._append_csv(self.logs_csv, record, ["timestamp", "agent_name", "task_id", "message"])
