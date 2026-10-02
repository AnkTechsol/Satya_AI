from .base import ExportAdapter
import requests
import threading
import queue
import atexit

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
                    "DD-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                }
                requests.post(self.url, json=item, headers=headers, timeout=2)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = [{
            "ddsource": "satya",
            "service": "satya-agent",
            "message": event_type,
            "agent_name": agent_name,
            "trace_id": trace_id,
            **data
        }]
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass

    def shutdown(self):
        if not self.worker.is_alive(): return
        self.queue.put(None)
        self.queue.join()
        self.worker.join()
