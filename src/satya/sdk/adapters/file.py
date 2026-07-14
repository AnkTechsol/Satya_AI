import json
import os
from .base import ExportAdapter

class FileExportAdapter(ExportAdapter):
    def __init__(self, filepath: str = "traces.jsonl"):
        self.filepath = filepath
        dirname = os.path.dirname(self.filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data.copy()
        }
        with open(self.filepath, "a") as f:
            f.write(json.dumps(payload) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
            "type": "log"
        }
        with open(self.filepath, "a") as f:
            f.write(json.dumps(payload) + "\n")
