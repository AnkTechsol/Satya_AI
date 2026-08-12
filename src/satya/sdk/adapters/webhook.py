import requests
import json
from datetime import datetime, timezone
from .base import ExportAdapter

class WebhookAdapter(ExportAdapter):
    """
    Webhook Adapter.
    Exports traces and logs by making POST requests to a specified Webhook URL.
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.endpoint_url:
            return

        payload = {
            "type": "trace",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data.copy()
        }
        try:
            requests.post(self.endpoint_url, json=payload, timeout=2)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        if not self.endpoint_url:
            return

        payload = {
            "type": "log",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "agent_name": agent_name,
            "task_id": task_id,
            "message": message
        }
        try:
            requests.post(self.endpoint_url, json=payload, timeout=2)
        except Exception:
            pass