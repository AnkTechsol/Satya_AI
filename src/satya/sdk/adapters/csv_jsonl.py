import csv
import json
import os
import threading
from datetime import datetime, timezone
from .base import ExportAdapter

class CSVJSONLExporter(ExportAdapter):
    """
    ExportAdapter for CSV and JSONL formats.
    """
    def __init__(self, export_dir: str = "satya_data/exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.csv_file = os.path.join(self.export_dir, "traces.csv")
        self.jsonl_file = os.path.join(self.export_dir, "traces.jsonl")
        self._lock = threading.Lock()

        with self._lock:
            if not os.path.exists(self.csv_file) or os.path.getsize(self.csv_file) == 0:
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        payload = data.copy()

        record = {
            "timestamp": now,
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": payload
        }

        with self._lock:
            with open(self.jsonl_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record) + "\n")

            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    now,
                    trace_id or "",
                    agent_name or "",
                    event_type or "",
                    json.dumps(payload)
                ])

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
