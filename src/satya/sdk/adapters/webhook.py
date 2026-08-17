import os
import json
import logging
import threading
import queue
import atexit
import requests
from datetime import datetime, timezone
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class WebhookExportAdapter(ExportAdapter):
    """
    Exports traces and logs to a webhook URL in the background.
    """
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.queue = queue.Queue()
        self.shutdown_event = threading.Event()

        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        atexit.register(self.shutdown)

    def _worker(self):
        while not self.shutdown_event.is_set():
            try:
                # Wait with timeout to allow checking shutdown_event
                payload = self.queue.get(timeout=1.0)
                try:
                    requests.post(self.webhook_url, json=payload, timeout=5)
                except Exception:
                    pass
                finally:
                    self.queue.task_done()
            except queue.Empty:
                continue

    def shutdown(self):
        self.shutdown_event.set()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        payload = {
            "type": "trace",
            "timestamp": timestamp,
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
        }
        self.queue.put(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        payload = {
            "type": "log",
            "timestamp": timestamp,
            "agent_name": agent_name,
            "task_id": task_id,
            "message": message
        }
        self.queue.put(payload)
