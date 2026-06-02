from .base import ExportAdapter
import json
import fcntl
import os

class OTLPJsonExporter(ExportAdapter):
    """
    JSONL Adapter.
    Exports traces to an append-only JSONL file.
    """
    def __init__(self, filepath: str = "otel-traces.jsonl"):
        self.filepath = filepath

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self.filepath, "a") as f:
                # Use fcntl for advisory file locking to prevent concurrent write corruption
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(json.dumps(payload) + "\n")
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        try:
            with open(self.filepath, "a") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(json.dumps(payload) + "\n")
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass