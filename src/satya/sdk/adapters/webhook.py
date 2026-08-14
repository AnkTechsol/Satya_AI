import logging
from urllib.parse import urlparse
import socket
import ipaddress
import requests
from requests.adapters import HTTPAdapter
from .base import ExportAdapter

logger = logging.getLogger(__name__)

class SSRFMitigationAdapter(HTTPAdapter):
    def __init__(self, target_ip, parsed_url, *args, **kwargs):
        self.target_ip = target_ip
        self.parsed_url = parsed_url
        super().__init__(*args, **kwargs)

    def get_connection(self, url, proxies=None):
        conn = super().get_connection(url, proxies)
        conn.host = self.target_ip
        if self.parsed_url.scheme == 'https':
            conn.assert_hostname = self.parsed_url.hostname
            conn.conn_kw['server_hostname'] = self.parsed_url.hostname
        return conn

class WebhookExportAdapter(ExportAdapter):
    """
    Exports traces and logs via HTTP webhooks, ensuring SSRF mitigations
    for enterprise security environments.
    """
    def __init__(self, url: str, auth_token: str = None):
        self.url = url
        self.auth_token = auth_token
        self.headers = {"Content-Type": "application/json"}
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def _is_safe_url(self, url: str) -> bool:
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

    def _send_webhook(self, payload: dict):
        if not self._is_safe_url(self.url):
            logger.warning(f"Webhook URL is unsafe or unresolvable: {self.url}")
            return

        parsed = urlparse(self.url)
        try:
            addr_info = socket.getaddrinfo(parsed.hostname, None)
            safe_ip = None
            for result in addr_info:
                ip_str = result[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                if ip_obj.is_global:
                    safe_ip = ip_str
                    break

            if not safe_ip:
                logger.warning(f"No global IP resolved for webhook URL: {self.url}")
                return

            with requests.Session() as session:
                adapter = SSRFMitigationAdapter(target_ip=safe_ip, parsed_url=parsed)
                session.mount("http://", adapter)
                session.mount("https://", adapter)

                session.post(
                    self.url,
                    json=payload,
                    timeout=5,
                    allow_redirects=False,
                    headers=self.headers
                )
        except Exception as e:
            # Swallow exceptions to prevent agent runtime crash
            logger.error(f"Failed to export via webhook: {e}")
            pass

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "type": "trace",
            "trace_id": trace_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "data": data.copy()
        }
        self._send_webhook(payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "type": "log",
            "agent_name": agent_name,
            "message": message,
            "task_id": task_id
        }
        self._send_webhook(payload)
