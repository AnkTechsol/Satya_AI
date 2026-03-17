import json
from .base import ExportAdapter

class OTLPAdapter(ExportAdapter):
    """Mock OTLP adapter that prints JSON lines to stdout."""
    def __init__(self, endpoint="http://localhost:4318/v1/traces"):
        self.endpoint = endpoint

    def _export(self, event_type: str, data: dict):
        payload = {
            "type": "otlp_mock",
            "endpoint": self.endpoint,
            "event": event_type,
            "data": data
        }
        print(f"[OTLP Adapter] {json.dumps(payload)}")

    def on_task_created(self, task: dict):
        self._export("task_created", {"id": task.get("id"), "title": task.get("title")})

    def on_task_updated(self, task: dict):
        self._export("task_updated", {"id": task.get("id"), "status": task.get("status")})

    def on_log(self, task_id: str, message: str):
        self._export("log_added", {"task_id": task_id, "message": message})
