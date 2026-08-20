import threading
import queue
import atexit
import requests
from datetime import datetime, timezone
from .base import ExportAdapter

class WebhookExportAdapter(ExportAdapter):
    """
    Webhook Export Adapter.
    Pushes traces and logs to a specified webhook URL asynchronously.
    """
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        atexit.register(self.shutdown)

    def _worker(self):
        while True:
            # Block waiting for an item
            payload = self.queue.get()

            if payload is None:
                # Poison pill received
                self.queue.task_done()
                break

            try:
                requests.post(self.target_url, json=payload, timeout=2)
            except Exception:
                # Swallow exceptions to prevent agent crashes from telemetry failures
                pass
            finally:
                self.queue.task_done()

    def shutdown(self):
        """Cleanly shutdown the worker thread."""
        self._shutdown_event.set()
        # Put poison pill to unblock the get
        self.queue.put(None)
        # Wait for queue to be fully processed
        self.queue.join()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
        }
        self.queue.put(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        self.queue.put(payload)
