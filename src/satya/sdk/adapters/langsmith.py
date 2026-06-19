from .base import ExportAdapter
import requests
import datetime
import uuid

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports trace events to LangSmith API.
    """
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com/runs"):
        self.api_key = api_key
        self.endpoint = endpoint

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "id": trace_id if trace_id else str(uuid.uuid4()),
            "name": event_type,
            "run_type": "chain",
            "start_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "extra": {
                "agent_name": agent_name,
                "metadata": data
            }
        }
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            requests.post(self.endpoint, json=payload, headers=headers, timeout=2)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
