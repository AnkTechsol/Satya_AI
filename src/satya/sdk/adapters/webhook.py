import threading
import queue
import atexit
import socket
import ipaddress
from urllib.parse import urlparse
import requests
import logging
from .base import ExportAdapter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WebhookAdapter(ExportAdapter):
    """
    Exports traces and logs to an HTTP webhook endpoint.
    Includes SSRF protection, background queueing, and graceful shutdown.
    """
    def __init__(self, endpoint_url: str):
        parsed = urlparse(endpoint_url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError("Endpoint URL must use http or https scheme")

        self.endpoint_url = endpoint_url
        self.scheme = parsed.scheme
        self.hostname = parsed.hostname
        self.port = parsed.port or (443 if self.scheme == 'https' else 80)
        self.path = parsed.path or '/'
        if parsed.query:
            self.path += '?' + parsed.query

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
                ip = socket.gethostbyname(self.hostname)
                ip_obj = ipaddress.ip_address(ip)
                if not ip_obj.is_global:
                    logger.warning(f"SSRF blocked: IP {ip} is not global")
                    continue

                safe_url = f"{self.scheme}://{ip}:{self.port}{self.path}"
                headers = {'Host': self.hostname, 'Content-Type': 'application/json'}
                requests.post(safe_url, json=item, headers=headers, timeout=5, verify=False)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
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
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "agent_name": agent_name,
            "task_id": task_id,
            "message": message
        }
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            pass

    def shutdown(self):
        if not self.worker.is_alive():
            return
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.queue.join()
        self.worker.join()
