from .base import ExportAdapter
import requests
import datetime
from datetime import timezone

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces and logs to the LangSmith observability platform.
    """
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com", project_name: str = "default"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.project_name = project_name

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.datetime.now(timezone.utc).isoformat()

        payload = {
            "id": trace_id or "satya-trace",
            "name": event_type,
            "run_type": "chain",
            "start_time": now,
            "extra": {
                "agent_name": agent_name,
                "project_name": self.project_name,
                **data
            }
        }

        try:
            requests.post(
                f"{self.endpoint}/runs",
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
