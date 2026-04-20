from .base import ExportAdapter
import datetime
import requests
import json

class OTLPAdapter(ExportAdapter):
    """
    OTLP Adapter.
    Uses opentelemetry-exporter-otlp to send Spans to Datadog/LangSmith.
    """
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or "http://localhost:4318/v1/traces"

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        payload = {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "satya-agent"}},
                            {"key": "agent.name", "value": {"stringValue": agent_name}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "spans": [
                                {
                                    "traceId": trace_id.ljust(32, '0')[:32] if trace_id else "0"*32,
                                    "spanId": trace_id.ljust(16, '0')[:16] if trace_id else "0"*16,
                                    "name": event_type,
                                    "kind": 1,
                                    "attributes": [{"key": k, "value": {"stringValue": str(v)}} for k, v in data.items()]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        try:
            requests.post(self.endpoint, json=payload, timeout=2)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        pass
