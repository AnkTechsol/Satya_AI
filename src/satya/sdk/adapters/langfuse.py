from .base import ExportAdapter
from ...core.schema import TraceEvent
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

        event = TraceEvent(trace_id=trace_id, agent_name=agent_name, event_type=event_type, data=data)

        payload = {
            "batch": [
                {
                    "id": event.trace_id or "satya-trace",
                    "type": "trace-create",
                    "timestamp": event.timestamp,
                    "body": {
                        "id": event.trace_id,
                        "name": event.event_type,
                        "metadata": {
                            "agent_name": event.agent_name,
                            **event.data
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
