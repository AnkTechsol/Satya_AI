import uuid
from .base import ExportAdapter
import requests
from datetime import datetime, timezone

class LangSmithAdapter(ExportAdapter):
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        # Ensure trace_id is a valid UUID
        try:
            valid_uuid = str(uuid.UUID(trace_id))
        except (ValueError, TypeError, AttributeError):
            valid_uuid = str(uuid.uuid4())

        now = datetime.now(timezone.utc).isoformat()

        inputs = data.get("prompt", {})
        outputs = data.get("response", {})

        # Map payload fields to LangSmith schema
        payload = {
            "id": valid_uuid,
            "name": event_type,
            "run_type": "llm" if "prompt" in data else "chain",
            "start_time": now,
            "end_time": now,
            "inputs": inputs if isinstance(inputs, dict) else {"prompt": inputs},
            "outputs": outputs if isinstance(outputs, dict) else {"response": outputs},
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    **data
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
