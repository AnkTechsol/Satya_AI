from .base import ExportAdapter
import requests
import uuid
from datetime import datetime, timezone

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces to LangSmith observability platform.
    """
    def __init__(self, api_key: str, project_name: str = "default", host: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.project_name = project_name
        self.host = host.rstrip("/")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.now(timezone.utc).isoformat()

        # Ensure trace_id is a strictly valid UUID
        try:
            val = uuid.UUID(trace_id, version=4)
            valid_id = str(val)
        except (ValueError, TypeError):
            valid_id = str(uuid.uuid4())

        payload = {
            "id": valid_id,
            "name": event_type,
            "run_type": "llm",
            "start_time": now,
            "end_time": now,
            "session_name": self.project_name,
            "inputs": {"prompt": data.get("prompt", "")} if "prompt" in data else data,
            "outputs": {"response": data.get("response", "")} if "response" in data else {"status": "ok"},
            "extra": {
                "agent_name": agent_name
            }
        }

        try:
            requests.post(
                f"{self.host}/runs",
                json=payload,
                headers={"x-api-key": self.api_key},
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
