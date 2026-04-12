from .base import ExportAdapter
import datetime
import requests

class OTLPAdapter(ExportAdapter):
    """
    Mock OTLP Adapter.
    In a real-world scenario, this would use opentelemetry-exporter-otlp to send Spans to Datadog/LangSmith.
    """
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or "http://localhost:4318/v1/traces"

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "resourceSpans": [{
                "scopeSpans": [{
                    "spans": [{
                        "traceId": trace_id,
                        "name": event_type,
                        "attributes": [{"key": k, "value": {"stringValue": str(v)}} for k, v in data.items()]
                    }]
                }]
            }]
        }
        try:
            requests.post(self.endpoint, json=payload, timeout=2)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        payload = {
            "resourceLogs": [{
                "scopeLogs": [{
                    "logRecords": [{
                        "body": {"stringValue": message},
                        "attributes": [
                            {"key": "agent.name", "value": {"stringValue": agent_name}},
                            {"key": "task.id", "value": {"stringValue": str(task_id)}}
                        ]
                    }]
                }]
            }]
        }
        try:
            requests.post(self.endpoint.replace("traces", "logs"), json=payload, timeout=2)
        except Exception:
            pass