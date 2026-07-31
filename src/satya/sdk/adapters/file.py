import json
import csv
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class CSVExportAdapter(ExportAdapter):
    def __init__(self, filepath: str = "traces.csv"):
        self.filepath = filepath
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                trace_id,
                agent_name,
                event_type,
                json.dumps(data)
            ])

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass

class JSONLExportAdapter(ExportAdapter):
    def __init__(self, filepath: str = "traces.jsonl"):
        self.filepath = filepath

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
        }
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(event) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
