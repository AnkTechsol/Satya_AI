import json
import os
from datetime import datetime, timezone
from .base import ExportAdapter

class OTLPAdapter(ExportAdapter):
    def __init__(self, filepath="traces.jsonl"):
        self.filepath = filepath

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, payload: dict) -> None:
        # Ensure parent directory exists safely
        dir_name = os.path.dirname(self.filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        now = datetime.now(timezone.utc).isoformat() + "Z"
        data = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "payload": payload,
            "timestamp": now,
            "format": "otlp-compat"
        }

        try:
            with open(self.filepath, 'a') as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(f"OTLP Adapter Error: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None) -> None:
        pass
