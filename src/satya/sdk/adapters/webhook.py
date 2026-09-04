from .base import ExportAdapter
import requests
import queue
import threading
import atexit
import logging

logger = logging.getLogger(__name__)

class WebhookExportAdapter(ExportAdapter):
    """
    Webhook Export Adapter.
    Exports traces and logs via HTTP requests.
    Dispatches network requests in a background worker thread.
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self.queue = queue.Queue()
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
                requests.post(self.endpoint_url, json=item, timeout=2)
            except Exception as e:
                # Swallow exceptions and prevent transient telemetry failures from crashing
                logger.debug(f"Webhook export failed: {e}")
                pass
            finally:
                self.queue.task_done()

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

    def shutdown(self):
        if not self.worker.is_alive():
            return

        # Disable accepting new items (optional, but good practice).
        # Using poison pill is standard.
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.queue.join()
        self.worker.join()