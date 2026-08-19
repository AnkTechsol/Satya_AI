import threading
import queue
import atexit
import requests
import time
from .base import ExportAdapter

class WebhookAdapter(ExportAdapter):
    """
    Exports events and logs asynchronously via webhooks.
    Uses a background thread and a queue to ensure non-blocking HTTP requests.
    """
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        atexit.register(self.shutdown)

    def _worker(self):
        while not self._shutdown_event.is_set():
            try:
                # Use a timeout so the thread can check the shutdown event periodically
                payload = self.queue.get(timeout=0.1)
                try:
                    requests.post(self.webhook_url, json=payload, timeout=5)
                except Exception:
                    pass  # Swallow transient errors to prevent agent runtime crash
                finally:
                    self.queue.task_done()
            except queue.Empty:
                continue

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data,
            "timestamp": time.time()
        }
        self.queue.put(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
            "timestamp": time.time()
        }
        self.queue.put(payload)

    def shutdown(self):
        """Gracefully shut down the background worker thread."""
        self._shutdown_event.set()
        # Ensure all queued items are processed
        self.queue.join()
        if self._worker_thread.is_alive():
            self._worker_thread.join()
