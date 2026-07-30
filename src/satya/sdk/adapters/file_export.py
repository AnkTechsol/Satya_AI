import json
import csv
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class JSONLExporter(ExportAdapter):
    def __init__(self, file_path: str = "satya_export.jsonl"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)) or ".", exist_ok=True)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload_data = data.copy()
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": payload_data
        }
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

class CSVExporter(ExportAdapter):
    def __init__(self, file_path: str = "satya_export.csv"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)) or ".", exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "type", "trace_id", "agent_name", "event_type", "task_id", "message", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload_data = data.copy()
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                "trace",
                trace_id,
                agent_name,
                event_type,
                "",
                "",
                json.dumps(payload_data)
            ])

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                "log",
                "",
                agent_name,
                "",
                task_id or "",
                message,
                ""
            ])
