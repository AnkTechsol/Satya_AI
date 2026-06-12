import json
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class OTLPFileAdapter(ExportAdapter):
    def __init__(self, filepath: str = "otel-traces.json"):
        self.filepath = filepath

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        dirname = os.path.dirname(self.filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        record = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "data": data
        }
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(record) + "\n")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
