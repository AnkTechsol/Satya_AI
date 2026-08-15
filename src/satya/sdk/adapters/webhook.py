import requests
import logging

from .base import ExportAdapter

logger = logging.getLogger(__name__)

class WebhookExportAdapter(ExportAdapter):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = data.copy()
        payload.update({
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type
        })
        self._send_webhook(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
            "event_type": "log"
        }
        self._send_webhook(payload)

    def _send_webhook(self, payload: dict):
            def send():
                try:
                    requests.post(
                        self.webhook_url,
                        json=payload,
                        timeout=5,
                        allow_redirects=False
                    )
                except Exception as e:
                    logger.error(f"Failed to export to webhook {self.webhook_url}: {e}")
                    pass
            import threading
            threading.Thread(target=send, daemon=True).start()
