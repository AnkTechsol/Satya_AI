from .base import ExportAdapter
import json
import csv
import os
import sys
import fcntl
from datetime import datetime, timezone

class CsvJsonlAdapter(ExportAdapter):
    """
    Export Adapter that writes traces to a CSV file and logs to a JSONL file.
    """
    def __init__(self, trace_file: str = "traces.csv", log_file: str = "logs.jsonl"):
        self.trace_file = trace_file
        self.log_file = log_file

        # Ensure trace file has headers if it doesn't exist or is empty
        if not os.path.exists(self.trace_file) or os.path.getsize(self.trace_file) == 0:
            with open(self.trace_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "trace_id", "agent_name", "event_type", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        try:
            with open(self.trace_file, mode='a', newline='') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    writer = csv.writer(f)
                    writer.writerow([now, trace_id, agent_name, event_type, json.dumps(data)])
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            sys.stderr.write(f"CsvJsonlAdapter failed to export trace: {e}\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "timestamp": now,
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        try:
            with open(self.log_file, mode='a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.write(json.dumps(payload) + "\n")
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            sys.stderr.write(f"CsvJsonlAdapter failed to export log: {e}\n")
