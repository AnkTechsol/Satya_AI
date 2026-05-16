from .base import ExportAdapter
import requests
import datetime
import uuid
import json

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces directly to the LangSmith API.
    """
    def __init__(self, api_key: str, project_name: str = "default", endpoint: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.project_name = project_name
        self.endpoint = endpoint.rstrip("/")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        # We need a run ID for Langsmith, if trace_id is not a valid UUID, create one.
        run_id = trace_id if trace_id else str(uuid.uuid4())
        try:
             uuid.UUID(run_id)
        except ValueError:
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
                    "satya_event": event_type,
                    **data
                }
            },
            "session_name": self.project_name,
            "inputs": data.get("inputs", {}),
            "outputs": data.get("outputs", {})
        }

        try:
            requests.post(
                f"{self.endpoint}/runs",
                headers=self.headers,
                json=payload,
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
