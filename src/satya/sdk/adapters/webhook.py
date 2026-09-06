import queue
import threading
import requests
import atexit
from .base import ExportAdapter

class WebhookExportAdapter(ExportAdapter):
    def __init__(self, endpoint_urls: list[str]):
        self.endpoint_urls = endpoint_urls
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

            trace_id, agent_name, event_type, data = item
            payload = {
                "trace_id": trace_id,
                "agent_name": agent_name,
                "event": event_type,
                "data": data
            }

            for url in self.endpoint_urls:
                try:
                    requests.post(url, json=payload, timeout=5)
                except Exception:
                    pass

            self.queue.task_done()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        try:
            self.queue.put_nowait((trace_id, agent_name, event_type, data))
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass

    def shutdown(self):
        if not self.worker.is_alive():
            return

        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass

        self.worker.join(timeout=2.0)
