import os
import json
import csv
from datetime import datetime, timezone
from .base import ExportAdapter

class FileExportAdapter(ExportAdapter):
    """
    File Export Adapter (CSV/JSONL).
    Exports traces to JSONL and logs to CSV.
    """
    def __init__(self, traces_filepath: str = "traces.jsonl", logs_filepath: str = "logs.csv"):
        self.traces_filepath = traces_filepath
        self.logs_filepath = logs_filepath
        self._ensure_file(self.traces_filepath)
        self._ensure_file(self.logs_filepath, is_csv=True)

    def _ensure_file(self, filepath: str, is_csv: bool = False):
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                if is_csv:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'agent_name', 'task_id', 'message'])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload_data = data.copy()
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": payload_data
        }
        with open(self.traces_filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        with open(self.logs_filepath, 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat() + "Z",
                agent_name,
                task_id or "",
                message
            ])
