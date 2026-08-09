from .base import ExportAdapter
import requests

class WebhookAdapter(ExportAdapter):
    """
    Webhook Adapter.
    Exports traces and logs to a specified HTTP webhook URL.
    """
    def __init__(self, url: str):
        self.url = url

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data.copy()
        }
        try:
            requests.post(self.url, json=payload, timeout=2)
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
            requests.post(self.url, json=payload, timeout=2)
        except Exception:
            pass
