import json
import logging
import queue
import threading
import atexit
from urllib.parse import urlparse
import requests

from .base import ExportAdapter

logger = logging.getLogger(__name__)

class WebhookAdapter(ExportAdapter):
    def __init__(self, webhook_url: str, max_queue_size: int = 1000):
        self.webhook_url = webhook_url
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        atexit.register(self.shutdown)

    def _is_safe_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            if not parsed.hostname:
                return False
            return True
        except Exception:
            return False

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data,
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            logger.warning("WebhookAdapter queue is full, dropping trace")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            logger.warning("WebhookAdapter queue is full, dropping log")

    def _worker_loop(self):
        while True:
            item = self.queue.get()
            if item is None:
                self.queue.task_done()
                break

            if not self._is_safe_url(self.webhook_url):
                logger.error(f"Invalid webhook URL: {self.webhook_url}")
                self.queue.task_done()
                continue

            try:
                # Use verify=True (default) for SSL verification
                requests.post(self.webhook_url, json=item, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send webhook: {e}")
                pass # Swallow exceptions so transient failures don't crash the core
            finally:
                self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return

        # Non-blocking clear of the queue to prevent deadlocks
        while True:
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break

        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass

        self.queue.join()
        self.worker.join()
