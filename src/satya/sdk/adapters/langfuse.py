from .base import ExportAdapter
import datetime
import requests

class LangfuseAdapter(ExportAdapter):
    def __init__(self, endpoint: str = None, public_key: str = None, secret_key: str = None):
        self.endpoint = endpoint or "https://cloud.langfuse.com"
        self.public_key = public_key
        self.secret_key = secret_key

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not self.public_key or not self.secret_key:
            return
        try:
            payload = {
                "batch": [{
                    "id": trace_id,
                    "type": "trace-create",
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "body": {
                        "name": f"{agent_name}-{event_type}",
                        "metadata": data
                    }
                }]
            }
            requests.post(f"{self.endpoint}/api/public/ingestion", json=payload, auth=(self.public_key, self.secret_key), timeout=2)
        except Exception as e:
            import logging
            logging.debug(f"Failed to export trace to Langfuse: {e}")
        except Exception as e:
            import logging
            logging.debug(f"Failed to export log to Langfuse: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        if not self.public_key or not self.secret_key:
            return
        try:
            payload = {
                "batch": [{
                    "type": "event-create",
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "body": {
                        "traceId": task_id or "global",
                        "name": "log",
                        "input": message
                    }
                }]
            }
            requests.post(f"{self.endpoint}/api/public/ingestion", json=payload, auth=(self.public_key, self.secret_key), timeout=2)
        except Exception:
            pass
