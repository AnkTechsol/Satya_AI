from .base import ExportAdapter
import requests
import datetime

class LangSmithAdapter(ExportAdapter):
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com", project_name: str = "default"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.project_name = project_name

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return
        payload = {
            "id": trace_id or "0"*32,
            "name": event_type,
            "project_name": self.project_name,
            "run_type": "chain",
            "start_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "extra": {"agent_name": agent_name},
            "inputs": data
        }
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            requests.post(f"{self.endpoint}/runs", json=payload, headers=headers, timeout=2, allow_redirects=False)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
