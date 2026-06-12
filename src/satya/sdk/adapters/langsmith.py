import json
import requests
from datetime import datetime, timezone
from .base import ExportAdapter

class LangSmithAdapter(ExportAdapter):
    def __init__(self, api_key: str, endpoint: str = "https://api.smith.langchain.com", project_name: str = "default"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.project_name = project_name

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.api_key:
            return

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        import logging
        logger = logging.getLogger(__name__)

        run_payload = {
            "id": trace_id,
            "name": event_type,
            "run_type": "chain",
            "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "extra": {
                "metadata": {
                    "agent_name": agent_name,
                    **data
                }
            },
            "session_name": self.project_name
        }

        try:
            requests.post(
                f"{self.endpoint}/runs",
                json=run_payload,
                headers=headers,
                timeout=2
            )
        except Exception as e:
            logger.debug(f"Failed to export trace to LangSmith: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
