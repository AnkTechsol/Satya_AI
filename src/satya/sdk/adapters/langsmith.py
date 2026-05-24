import requests
import json
from .base import ExportAdapter
import time
import uuid

class LangSmithAdapter(ExportAdapter):
    def __init__(self, api_url: str = "https://api.smith.langchain.com", api_key: str = None):
        """
        Initialize the LangSmith adapter.
        :param api_url: LangSmith API URL.
        :param api_key: LangSmith API key (LANGCHAIN_API_KEY).
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        if not self.api_key:
            import os
            self.api_key = os.environ.get("LANGCHAIN_API_KEY", "")

    def _post(self, endpoint: str, payload: dict):
        if not self.api_key:
            return

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            requests.post(
                f"{self.api_url}/{endpoint.lstrip('/')}",
                json=payload,
                headers=headers,
                timeout=2
            )
        except Exception:
            # Silently fail on timeout or connection issues to avoid breaking core loop
            pass

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        """
        Export a trace to LangSmith as a run.
        """
        run_id = str(uuid.uuid4())
        now = time.time()

        payload = {
            "id": run_id,
            "name": event_type,
            "run_type": "chain",
            "start_time": now,
            "end_time": now,
            "extra": {
                "metadata": {
                    "trace_id": trace_id,
                    "agent_name": agent_name,
                    **data
                }
            }
        }
        self._post("/runs", payload)

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        """
        Export a log entry to LangSmith as a simple run.
        """
        run_id = str(uuid.uuid4())
        now = time.time()

        payload = {
            "id": run_id,
            "name": "log",
            "run_type": "tool",
            "start_time": now,
            "end_time": now,
            "inputs": {"message": message},
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    "task_id": task_id
                }
            }
        }
        self._post("/runs", payload)
