import queue
import threading
import atexit
import json
import logging
import requests
from typing import Dict, Any, Optional
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class DatadogAdapter(ExportAdapter):
    def __init__(self, api_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.site = site
        self.log_endpoint = f"https://http-intake.logs.{site}/api/v2/logs"
        self.headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key
        }
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
                self._send_payload(item)
            except Exception as e:
                logger.error(f"DatadogAdapter export failed: {e}")
            finally:
                self.queue.task_done()

    def _send_payload(self, payload: Dict[str, Any]):
        try:
            requests.post(self.log_endpoint, headers=self.headers, json=payload, timeout=5)
        except Exception:
            pass

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "ddsource": "satya-agent",
            "ddtags": f"agent:{agent_name},event_type:{event_type}",
            "message": f"Trace: {event_type}",
            "trace_id": trace_id,
            "data": data
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: Optional[str] = None):
        payload = {
            "ddsource": "satya-agent",
            "ddtags": f"agent:{agent_name}",
            "message": message,
            "task_id": task_id
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def shutdown(self):
        if not self.worker.is_alive():
            return
        # clear queue to unblock shutdown if full
        while True:
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.queue.join()
        self.worker.join(timeout=2)
