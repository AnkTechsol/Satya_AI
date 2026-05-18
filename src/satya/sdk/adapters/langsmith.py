from .base import ExportAdapter
import requests
from datetime import datetime, timezone
import json
import uuid

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces to LangSmith observability platform.
    """
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com", project_name: str = "default"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.project_name = project_name

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.now(timezone.utc).isoformat()

        # In LangSmith, a trace is typically a run. We create a Run representing the event.
        run_id = str(uuid.uuid4())

        payload = {
            "id": run_id,
            "name": event_type,
            "run_type": "chain", # or tool/llm
            "start_time": now,
            "end_time": now,
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    **data
                }
            },
            "session_name": self.project_name,
            "trace_id": trace_id or run_id
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            requests.post(
                f"{self.endpoint}/runs",
                json=payload,
                headers=headers,
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass