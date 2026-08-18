import queue
import threading
import atexit
import requests
import json
from .base import ExportAdapter

class WebhookAdapter(ExportAdapter):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        atexit.register(self.shutdown)

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                payload = self.queue.get(timeout=1.0)
                try:
                    requests.post(self.webhook_url, json=payload, timeout=5.0)
                except Exception:
                    pass
                self.queue.task_done()
            except queue.Empty:
                continue

    def shutdown(self):
        self.stop_event.set()
        # Ensure any remaining tasks are processed before shutdown
        self.queue.join()
        self.worker_thread.join(timeout=2.0)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data,
            "type": "trace"
        }
        self.queue.put(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id,
            "type": "log"
        }
        self.queue.put(payload)
