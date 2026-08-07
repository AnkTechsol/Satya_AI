import os
import json
import csv
from datetime import datetime, timezone
from .base import ExportAdapter

class CSVJSONLExportAdapter(ExportAdapter):
    """
    Exports traces and logs to CSV and JSONL files for local analytics or data lakes.
    """
    def __init__(self, export_dir: str = "satya_data/export"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir, exist_ok=True)

        self.traces_csv = os.path.join(self.export_dir, "traces.csv")
        self.logs_csv = os.path.join(self.export_dir, "logs.csv")
        self.traces_jsonl = os.path.join(self.export_dir, "traces.jsonl")
        self.logs_jsonl = os.path.join(self.export_dir, "logs.jsonl")

        if not os.path.exists(self.traces_csv):
            with open(self.traces_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data"])

        if not os.path.exists(self.logs_csv):
            with open(self.logs_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "agent_name", "task_id", "message"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        data_copy = data.copy()

        with open(self.traces_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, trace_id, agent_name, event_type, json.dumps(data_copy)])

        with open(self.traces_jsonl, 'a', encoding='utf-8') as f:
            record = {
                "timestamp": timestamp,
                "trace_id": trace_id,
                "agent_name": agent_name,
                "event_type": event_type,
                "data": data_copy
            }
            f.write(json.dumps(record) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"

        with open(self.logs_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, agent_name, task_id or "", message])

        with open(self.logs_jsonl, 'a', encoding='utf-8') as f:
            record = {
                "timestamp": timestamp,
                "agent_name": agent_name,
                "task_id": task_id,
                "message": message
            }
            f.write(json.dumps(record) + "\n")
