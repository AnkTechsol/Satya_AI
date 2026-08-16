from .base import ExportAdapter
import requests
import threading
import queue
import atexit
from datetime import datetime, timezone

class WebhookExportAdapter(ExportAdapter):
    """
    Webhook Export Adapter.
    Sends traces and logs via HTTP POST to a configured webhook URL.
    Uses a background worker thread to prevent unbounded thread creation.
    """
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        atexit.register(self.shutdown)

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                # Use a timeout to periodically check the stop event
                payload = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                requests.post(self.webhook_url, json=payload, timeout=2)
            except Exception:
                pass
            finally:
                self._queue.task_done()

    def _send_payload(self, payload: dict):
        self._queue.put(payload)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data.copy()
        }
        self._send_payload(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "agent_name": agent_name,
            "task_id": task_id,
            "message": message
        }
        self._send_payload(payload)

    def shutdown(self):
        """Signals the background thread to stop and waits for the queue to drain."""
        # drain queue before stopping
        self._queue.join()
        self._stop_event.set()
        self._worker_thread.join(timeout=2.0)
