import queue
import threading
import atexit
import logging
import json
from .base import ExportAdapter
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WebhookExportAdapter(ExportAdapter):
    """
    Webhook Export Adapter.
    Exports traces and logs via HTTP POST to a webhook endpoint using a background worker thread.
    """
    def __init__(self, webhook_url: str, maxsize: int = 1000):
        self.webhook_url = webhook_url
        self.queue = queue.Queue(maxsize=maxsize)
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
                    session.post(self.webhook_url, json=item, timeout=2)
                except Exception as e:
                    logger.warning(f"Failed to export to webhook: {e}")
                finally:
                    self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return
        # To avoid unbounded blocking during shutdown, we clear the pending items
        # and only process the poison pill.
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.worker.join(timeout=2.0)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.webhook_url:
            return

        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "timestamp": now,
            "data": data
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        if not self.webhook_url:
            return

        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
            "timestamp": now
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass
