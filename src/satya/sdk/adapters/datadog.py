import threading
import queue
import atexit
import requests
from .base import ExportAdapter

class DatadogAdapter(ExportAdapter):
    def __init__(self, api_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.url = f"https://http-intake.logs.{site}/api/v2/logs"
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
                headers = {
                    "Content-Type": "application/json",
                    "DD-API-KEY": self.api_key
                }
                requests.post(self.url, json=item, headers=headers, timeout=5)
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
            "ddsource": "satya",
            "ddtags": f"env:prod,agent:{agent_name}",
            "message": f"Trace event: {event_type}",
            "trace_id": trace_id,
            "event_type": event_type,
            "data": data
        }
        try:
            self.queue.put_nowait([payload])
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "ddsource": "satya",
            "ddtags": f"env:prod,agent:{agent_name}",
            "message": message,
            "task_id": task_id
        }
        try:
            self.queue.put_nowait([payload])
        except queue.Full:
            pass
