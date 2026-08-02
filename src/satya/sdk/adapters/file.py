import csv
import json
import os
from .base import ExportAdapter
from datetime import datetime, timezone

class CSVJSONLExportAdapter(ExportAdapter):
    """
    Export Adapter for CSV and JSONL formats.
    """
    def __init__(self, filepath: str, format: str = "jsonl"):
        self.filepath = filepath
        self.format = format.lower()
        if self.format not in ["csv", "jsonl"]:
            raise ValueError("format must be 'csv' or 'jsonl'")

        # Initialize file with headers if it's CSV and doesn't exist
        if self.format == "csv" and not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()

        if self.format == "csv":
            with open(self.filepath, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([now, trace_id, agent_name, event_type, json.dumps(data)])
        elif self.format == "jsonl":
            with open(self.filepath, "a") as f:
                payload = {
                    "timestamp": now,
                    "trace_id": trace_id,
                    "agent_name": agent_name,
                    "event_type": event_type,
                    "data": data
                }
                f.write(json.dumps(payload) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        # We can optionally implement log export here as well, but for simplicity, we'll ignore it.
        pass
