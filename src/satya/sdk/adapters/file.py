import json
import csv
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class FileAdapter(ExportAdapter):
    """
    File Adapter.
    Exports traces and logs to local CSV and JSONL files.
    """
    def __init__(self, output_dir: str = "satya_data/exports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.traces_jsonl = os.path.join(self.output_dir, "traces.jsonl")
        self.traces_csv = os.path.join(self.output_dir, "traces.csv")
        self.logs_jsonl = os.path.join(self.output_dir, "logs.jsonl")

        if not os.path.exists(self.traces_csv):
            with open(self.traces_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data_json"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        payload_data = data.copy()

        trace_record = {
            "timestamp": now,
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": payload_data
        }
        with open(self.traces_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_record) + "\n")

        with open(self.traces_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([now, trace_id, agent_name, event_type, json.dumps(payload_data)])

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        now = datetime.now(timezone.utc).isoformat()
        log_record = {
            "timestamp": now,
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        with open(self.logs_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_record) + "\n")
