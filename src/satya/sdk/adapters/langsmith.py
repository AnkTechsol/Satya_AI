import os
import uuid
import json
import requests
import datetime
from .base import ExportAdapter

class LangSmithAdapter(ExportAdapter):
    def __init__(self):
        self.api_key = os.environ.get("LANGSMITH_API_KEY", "")
        self.project_name = os.environ.get("LANGSMITH_PROJECT", "default")
        self.endpoint = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

    def _ensure_uuid(self, id_str):
        if not id_str or id_str == 'unknown':
            return str(uuid.uuid4())
        try:
            val = uuid.UUID(id_str, version=4)
            return str(val)
        except ValueError:
            return str(uuid.uuid4())

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        run_id = self._ensure_uuid(trace_id)

        # Determine mapping based on event type
        run_type = "llm" if event_type == "prompt" else "chain"
        inputs = data.get("prompt", data) if event_type == "prompt" else {"data": data}
        outputs = data.get("response", {}) if event_type == "prompt" else {}

        now = datetime.datetime.utcnow().isoformat()

        payload = {
            "id": run_id,
            "name": f"{agent_name}_{event_type}",
            "run_type": run_type,
            "inputs": inputs,
            "outputs": outputs,
            "project_name": self.project_name,
            "start_time": now,
            "end_time": now,
        }

        try:
            requests.post(
                f"{self.endpoint}/runs",
                json=payload,
                headers={"x-api-key": self.api_key},
                timeout=2
            )
        except Exception:
            pass # fail silently

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass # Not implemented for langsmith yet
