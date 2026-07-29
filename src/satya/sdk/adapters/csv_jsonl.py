import csv
import json
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class CsvJsonlAdapter(ExportAdapter):
    """
    CSV/JSONL Adapter.
    Exports traces to dual CSV and JSONL flat files for zero-infra observability.
    """
    def __init__(self, export_dir: str):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.csv_path = os.path.join(self.export_dir, "traces.csv")
        self.jsonl_path = os.path.join(self.export_dir, "traces.jsonl")

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["trace_id", "agent_name", "event_type", "timestamp", "data"])

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        payload_data = data.copy()

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([trace_id, agent_name, event_type, now, json.dumps(payload_data)])

        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            record = {
                "trace_id": trace_id,
                "agent_name": agent_name,
                "event_type": event_type,
                "timestamp": now,
                "data": payload_data
            }
            f.write(json.dumps(record) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
