from .base import ExportAdapter
import requests
from datetime import datetime, timezone
import uuid

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

        now = datetime.now(timezone.utc).isoformat()

        # We need a unique run ID for Langsmith. If trace_id is missing or "unknown", generate one
        run_id = trace_id if (trace_id and trace_id != "unknown") else str(uuid.uuid4())

        # Ensure UUID format, naive check
        if len(run_id) != 36:
            run_id = str(uuid.uuid4())

        payload = {
            "id": run_id,
            "name": event_type,
            "run_type": "llm" if event_type == "trace_prompt" else "chain",
            "start_time": now,
            "end_time": now, # Simple instantaneous span
            "inputs": {"prompt": data.get("prompt")} if "prompt" in data else data,
            "outputs": {"response": data.get("response")} if "response" in data else None,
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    "tokens": data.get("tokens", 0)
                }
            }
        }

        try:
            res = requests.post(
                f"{self.endpoint}/runs",
                json=payload,
                headers={"x-api-key": self.api_key},
                timeout=2
            )
            res.raise_for_status()
        except Exception as e:
            # Explicitly swallow but one could log it
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
