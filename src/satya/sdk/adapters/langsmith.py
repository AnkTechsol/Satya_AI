from .base import ExportAdapter
import requests
import uuid
from datetime import datetime, timezone

class LangSmithAdapter(ExportAdapter):
    """
    LangSmith Adapter.
    Exports traces to LangSmith observability platform.
    """
    def __init__(self, api_key: str, project_name: str, host: str = "https://api.smith.langchain.com"):
        self.api_key = api_key
        self.project_name = project_name
        self.host = host.rstrip("/")

    def _ensure_valid_uuid(self, trace_id: str) -> str:
        """LangSmith requires valid UUID strings for the run ID."""
        if not trace_id or trace_id.lower() == "unknown":
            return str(uuid.uuid4())
        try:
            val = uuid.UUID(trace_id, version=4)
            return str(val)
        except ValueError:
            return str(uuid.uuid4())

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        run_id = self._ensure_valid_uuid(trace_id)
        now = datetime.now(timezone.utc).isoformat()

        # Map 'prompt' and 'response' to 'inputs' and 'outputs' per memory instruction
        # Use a copy to avoid mutating the original data dictionary
        payload_data = data.copy()

        inputs = {}
        if "prompt" in payload_data:
            inputs["prompt"] = payload_data.pop("prompt")
        else:
            inputs = {"data": payload_data}

        outputs = {}
        if "response" in payload_data:
            outputs["response"] = payload_data.pop("response")

        run_type = "llm" if "prompt" in inputs else "chain"

        payload = {
            "id": run_id,
            "name": event_type,
            "run_type": run_type,
            "start_time": now,
            "end_time": now, # Include end_time to prevent traces remaining stuck in pending state
            "inputs": inputs,
            "outputs": outputs,
            "session_name": self.project_name,
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    **payload_data
                }
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
