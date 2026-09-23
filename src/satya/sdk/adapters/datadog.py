import os
import json
import queue
import threading
import atexit
import requests
import logging
from datetime import datetime, timezone
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class DatadogAdapter(ExportAdapter):
    """
    Datadog Adapter.
    Exports traces and logs to Datadog's HTTP API asynchronously using a background worker.
    """
    def __init__(self, api_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.site = site
        self.url = f"https://http-intake.logs.{self.site}/api/v2/logs"
        self.queue = queue.Queue(maxsize=1000)
        self.worker = threading.Thread(target=self._process_queue, daemon=True)
        self.worker.start()
        atexit.register(self.shutdown)

    def _process_queue(self):
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key
        }
        while True:
            item = self.queue.get()
            if item is None:
                self.queue.task_done()
                break

            try:
                requests.post(self.url, json=item, headers=headers, timeout=5)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return

        try:
            while True:
                self.queue.get_nowait()
                self.queue.task_done()
        except queue.Empty:
            pass

        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass

        self.queue.join()
        self.worker.join()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        payload = {
            "ddsource": "satya_ai",
            "ddtags": f"env:production,agent:{agent_name}",
            "hostname": agent_name,
            "service": "satya_trace",
            "message": f"Trace event: {event_type}",
            "trace_id": trace_id,
            "event_type": event_type,
            **data
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        if not self.api_key:
            return

        payload = {
            "ddsource": "satya_ai",
            "ddtags": f"env:production,agent:{agent_name}",
            "hostname": agent_name,
            "service": "satya_log",
            "message": message,
            "task_id": task_id
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass
