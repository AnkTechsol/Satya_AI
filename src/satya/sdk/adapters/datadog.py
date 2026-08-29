import queue
import threading
import atexit
import requests
from typing import Optional
from datetime import datetime, timezone
from .base import ExportAdapter

class DatadogAdapter(ExportAdapter):
    """
    Datadog Adapter.
    Exports traces and logs to Datadog observability platform via HTTP API in a background thread.
    """
    def __init__(self, api_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.site = site
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
                url, payload = item
                headers = {
                    "DD-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                }
                requests.post(url, json=payload, headers=headers, timeout=2)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return
        self.queue.put(None)
        self.queue.join()
        self.worker.join()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        tags = f"agent:{agent_name},event:{event_type},trace_id:{trace_id}"

        payload = [{
            "ddsource": "satya-trace",
            "ddtags": tags,
            "hostname": "satya-agent",
            "message": f"Trace event: {event_type}",
            "trace_data": data
        }]
        try:
            self.queue.put_nowait((f"https://http-intake.logs.{self.site}/api/v2/logs", payload))
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: Optional[str] = None):
        if not self.api_key:
            return

        tags = f"agent:{agent_name}"
        if task_id:
            tags += f",task_id:{task_id}"

        payload = [{
            "ddsource": "satya",
            "ddtags": tags,
            "hostname": "satya-agent",
            "message": message
        }]

        try:
            self.queue.put_nowait((f"https://http-intake.logs.{self.site}/api/v2/logs", payload))
        except queue.Full:
            pass
