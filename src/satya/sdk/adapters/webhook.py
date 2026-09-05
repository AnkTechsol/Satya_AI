import json
import logging
import queue
import threading
import atexit
import requests
import socket
import ipaddress
from urllib.parse import urlparse
from .base import ExportAdapter

logger = logging.getLogger(__name__)

def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    try:
        addr_info = socket.getaddrinfo(parsed.hostname, None)
        for result in addr_info:
            ip_str = result[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if not ip_obj.is_global:
                return False
        return True
    except Exception:
        return False

class WebhookAdapter(ExportAdapter):
    """
    Webhook Export Adapter.
    Exports traces and logs to an external HTTP webhook endpoint in a background thread.
    """
    def __init__(self, url: str):
        self.url = url
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

            try:
                if not _is_safe_url(self.url):
                    logger.warning(f"Skipping unsafe webhook URL: {self.url}")
                    continue

                headers = {"Content-Type": "application/json"}
                requests.post(self.url, json=item, timeout=5, headers=headers)
            except Exception as e:
                logger.error(f"Failed to export via webhook to {self.url}: {e}")
            finally:
                self.queue.task_done()

    def shutdown(self):
        if not self.worker.is_alive():
            return

        # Wait for pending items to be processed
        self.queue.join()

        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.worker.join(timeout=2)

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass