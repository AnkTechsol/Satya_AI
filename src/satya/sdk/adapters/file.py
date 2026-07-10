import os
import json
from .base import ExportAdapter

class FileAdapter(ExportAdapter):
    def __init__(self, filepath="traces.jsonl"):
        self.filepath = filepath
        dir_name = os.path.dirname(self.filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self.filepath, "a") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        try:
            with open(self.filepath, "a") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            pass
