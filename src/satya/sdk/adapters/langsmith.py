from .base import ExportAdapter
import requests
import uuid
from datetime import datetime, timezone

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces to LangSmith observability platform.
    """
    def __init__(self, api_key: str, project_name: str = "default"):
        self.api_key = api_key
        self.project_name = project_name
        self.endpoint = "https://api.smith.langchain.com/runs"

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        run_id = str(uuid.uuid4())

        # Determine valid trace_id UUID
        valid_trace_id = trace_id
        try:
            uuid.UUID(valid_trace_id)
        except (ValueError, TypeError):
            valid_trace_id = str(uuid.uuid4())

        now = datetime.now(timezone.utc).isoformat()

        inputs = data.get("prompt") or data
        outputs = data.get("response")

        payload = {
            "id": run_id,
            "name": event_type,
            "start_time": now,
            "end_time": now,
            "run_type": "llm" if event_type == "prompt_trace" else "chain",
            "trace_id": valid_trace_id,
            "project_name": self.project_name,
            "inputs": {"inputs": inputs} if not isinstance(inputs, dict) else inputs,
            "outputs": {"outputs": outputs} if outputs and not isinstance(outputs, dict) else outputs,
            "extra": {
                "metadata": {
                    "agent_name": agent_name
                }
            }
        }

        try:
            requests.post(
                self.endpoint,
                json=payload,
                headers={"x-api-key": self.api_key},
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
