from .base import ExportAdapter
import requests
import json
from datetime import datetime, timezone
import uuid

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces and log events to LangSmith.
    """
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.now(timezone.utc).isoformat()

        # Simple POST to LangSmith's run endpoint to create a span
        payload = {
            "id": str(uuid.uuid4()),
            "name": event_type,
            "run_type": "chain",
            "start_time": now,
            "end_time": now,
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    "trace_id": trace_id,
                    **data
                }
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
