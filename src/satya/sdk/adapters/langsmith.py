from .base import ExportAdapter
import requests
from datetime import datetime, timezone

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces to LangSmith observability platform.
    """
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "id": trace_id or "satya-trace",
            "name": event_type,
            "start_time": now,
            "run_type": "llm",
            "extra": {
                "agent_name": agent_name,
                "metadata": data
            }
        }

        try:
            requests.post(
                f"{self.endpoint}/runs",
                json=payload,
                headers={"x-api-key": self.api_key},
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass