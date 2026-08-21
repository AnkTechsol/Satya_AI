import queue
import threading
import atexit
import requests
import json
from .base import ExportAdapter

class WebhookExportAdapter(ExportAdapter):
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
            self._send_payload(item)
            self.queue.task_done()

    def _send_payload(self, payload: dict):
        try:
            requests.post(self.endpoint_url, json=payload, timeout=5)
        except Exception:
            pass

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

    def shutdown(self):
        if not self.worker.is_alive():
            return
        self.queue.put(None)
        self.queue.join()
        self.worker.join(timeout=2)
