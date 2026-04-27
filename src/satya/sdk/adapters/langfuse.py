from .base import ExportAdapter
import requests
from datetime import datetime, timezone

class LangfuseAdapter(ExportAdapter):
    """
    Langfuse Adapter.
    Exports traces to Langfuse observability platform.
    """
    def __init__(self, public_key: str, secret_key: str, host: str = "https://cloud.langfuse.com"):
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host.rstrip("/")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        # Maps Satya event to Langfuse Trace/Span format
        if not self.public_key or not self.secret_key:
            return

        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "batch": [
                {
                    "id": trace_id or "satya-trace",
                    "type": "trace-create",
                    "timestamp": now,
                    "body": {
                        "id": trace_id,
                        "name": event_type,
                        "metadata": {
                            "agent_name": agent_name,
                            **data
                        }
                    }
                }
            ]
        }

        try:
            requests.post(
                f"{self.host}/api/public/ingestion",
                json=payload,
                auth=(self.public_key, self.secret_key),
                timeout=2
            )
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
