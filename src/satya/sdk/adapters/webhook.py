import threading
import queue
import atexit
import requests
import logging
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class WebhookExportAdapter(ExportAdapter):
    def __init__(self, webhook_url: str, timeout: int = 2):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.queue = queue.Queue(maxsize=1000)
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        atexit.register(self.shutdown)

    def _worker_loop(self):
        while True:
            item = self.queue.get()
            if item is None:
                self.queue.task_done()
                break

            try:
                requests.post(self.webhook_url, json=item, timeout=self.timeout)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.queue.join()
        self.worker.join()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
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
            "task_id": task_id
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass
