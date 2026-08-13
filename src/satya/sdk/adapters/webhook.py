import logging
import requests
from typing import Dict, Any, Optional
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class WebhookAdapter(ExportAdapter):
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 5):
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        # Using a session for connection pooling if multiple events are fired
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data.copy() if data else {}
        }
        self._send_payload(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        self._send_payload(payload)

    def _send_payload(self, payload: dict):
        try:
            self.session.post(self.url, json=payload, timeout=self.timeout)
        except Exception as e:
            logger.debug(f"WebhookAdapter failed to send payload to {self.url}: {e}")
