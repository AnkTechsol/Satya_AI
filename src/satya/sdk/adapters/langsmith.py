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
    def __init__(self, api_key: str, project_name: str = "default", endpoint: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.project_name = project_name
        self.endpoint = endpoint.rstrip("/")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.now(timezone.utc).isoformat()

        # We simulate a LangSmith run payload
        # It expects an ID (uuid), name, run_type, etc.
        run_id = trace_id if trace_id and len(trace_id) == 36 else str(uuid.uuid4())

        payload = {
            "id": run_id,
            "name": event_type,
            "run_type": "tool",
            "start_time": now,
            "end_time": now,
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    **data
                }
            },
            "session_name": self.project_name
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
