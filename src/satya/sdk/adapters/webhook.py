import json
import threading
import queue
import atexit
from datetime import datetime, timezone
import requests
from .base import ExportAdapter

class WebhookExportAdapter(ExportAdapter):
    """
    Webhook Export Adapter.
    Exports traces and logs via HTTP webhook requests asynchronously using a background worker thread.
    """
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        atexit.register(self.shutdown)

    def _worker_loop(self):
        while True:
            item = self.queue.get()
            if item is None:  # Poison pill
                self.queue.task_done()
                break

            try:
                headers = {"Content-Type": "application/json"}
                # Disallow arbitrary redirects to prevent some forms of SSRF and use timeout
                requests.post(self.webhook_url, json=item, headers=headers, timeout=5, allow_redirects=False)
            except Exception:
                pass  # Swallow telemetry errors
            finally:
                self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return
        # Put poison pill to break the loop
        self.queue.put(None)
        # Wait for all tasks to be processed
        self.queue.join()
        self.worker.join()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.webhook_url:
            return

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
        if not self.webhook_url:
            return

        payload = {
            "type": "log",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "agent_name": agent_name,
            "task_id": task_id,
            "message": message
        }
        self.queue.put(payload)
