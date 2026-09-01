import queue
import threading
import atexit
import requests
import json
import logging
from datetime import datetime, timezone
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class WebhookAdapter(ExportAdapter):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        atexit.register(self.shutdown)

    def _worker_loop(self):
        with requests.Session() as session:
            while True:
                item = self.queue.get()
                if item is None:
                    self.queue.task_done()
                    break
                try:
                    session.post(self.webhook_url, json=item, timeout=5)
                except Exception as e:
                    logger.debug(f"WebhookAdapter failed to send item: {e}")
                finally:
                    self.queue.task_done()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def shutdown(self):
        if not self.worker.is_alive():
            return
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.queue.join()
        self.worker.join(timeout=5)
