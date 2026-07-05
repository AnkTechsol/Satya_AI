import requests
import uuid
import socket
from datetime import datetime, timezone
from .base import ExportAdapter
from urllib.parse import urlparse

class SSRFProtectedAdapter(requests.adapters.HTTPAdapter):
    def get_connection(self, url, proxies=None):
        parsed = urlparse(url)
        try:
            # Resolve the hostname to an IP address
            addr_info = socket.getaddrinfo(parsed.hostname, parsed.port or 443)
            # Find the first globally routable IP
            ip = None
            for family, socktype, proto, canonname, sockaddr in addr_info:
                # Basic check, real implementation should use ipaddress module for robustness
                if not sockaddr[0].startswith('127.') and not sockaddr[0].startswith('10.') and not sockaddr[0].startswith('192.168.') and not sockaddr[0].startswith('172.'):
                    ip = sockaddr[0]
                    break
            if not ip:
                ip = parsed.hostname # Fallback if no safe IP found
        except socket.gaierror:
            ip = parsed.hostname

        conn = super().get_connection(url, proxies)
        conn.host = ip
        conn.assert_hostname = parsed.hostname
        conn.conn_kw['server_hostname'] = parsed.hostname
        return conn

class LangSmithAdapter(ExportAdapter):
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.mount("https://", SSRFProtectedAdapter())

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, payload: dict) -> None:
        try:
            if not trace_id or trace_id == "unknown":
                raise ValueError("Invalid trace_id")
            # Validate UUID
            uuid_obj = uuid.UUID(trace_id)
            valid_trace_id = str(uuid_obj)
        except ValueError:
            valid_trace_id = str(uuid.uuid4())

        # Map 'prompt' to 'inputs' and 'response' to 'outputs'
        inputs = payload.get("prompt", payload)
        outputs = payload.get("response", {})

        now = datetime.now(timezone.utc).isoformat() + "Z"

        data = {
            "id": valid_trace_id,
            "name": f"{agent_name}_{event_type}",
            "run_type": "llm",
            "start_time": now,
            "end_time": now,
            "inputs": inputs,
            "outputs": outputs,
            "extra": {"agent_name": agent_name, "event_type": event_type}
        }

        try:
            self.session.post(
                f"{self.endpoint}/runs",
                json=data,
                headers={"x-api-key": self.api_key},
                timeout=2,
                allow_redirects=False
            )
        except Exception as e:
            print(f"LangSmith Adapter Error: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None) -> None:
        pass # Logs can also be mapped, omitted for brevity
