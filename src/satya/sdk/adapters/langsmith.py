import uuid
import requests
from datetime import datetime, timezone
from .base import ExportAdapter

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

        if not trace_id or trace_id == "unknown":
            run_id = str(uuid.uuid4())
        else:
            try:
                run_id = str(uuid.UUID(trace_id))
            except (ValueError, TypeError):
                run_id = str(uuid.uuid4())

        now = datetime.now(timezone.utc).isoformat()

        run_type = "llm" if event_type == "prompt" else "chain"

        if event_type == "prompt":
            inputs = data.get("prompt", data)
            outputs = data.get("response", {})
        else:
            inputs = data
            outputs = {}

        payload = {
            "id": run_id,
            "name": event_type,
            "run_type": run_type,
            "start_time": now,
            "end_time": now,
            "inputs": inputs,
            "outputs": outputs,
            "extra": {
                "metadata": {
                    "agent_name": agent_name
                }
            }
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
