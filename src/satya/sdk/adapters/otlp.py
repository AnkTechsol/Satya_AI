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
        try:
            payload = {
                "resourceSpans": [{
                    "resource": {
                        "attributes": [{"key": "service.name", "value": {"stringValue": agent_name}}]
                    },
                    "scopeSpans": [{
                        "spans": [{
                            "traceId": trace_id.ljust(32, '0'),
                            "spanId": trace_id.ljust(16, '0'),
                            "name": event_type,
                            "attributes": [{"key": k, "value": {"stringValue": str(v)}} for k, v in data.items()]
                        }]
                    }]
                }]
            }
            requests.post(self.endpoint, json=payload, timeout=2)
        except Exception as e:
            import logging
            logging.debug(f"Failed to export trace to OTLP: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        try:
            payload = {
                "resourceLogs": [{
                    "resource": {
                        "attributes": [{"key": "service.name", "value": {"stringValue": agent_name}}]
                    },
                    "scopeLogs": [{
                        "logRecords": [{
                            "traceId": task_id.ljust(32, '0') if task_id else "".ljust(32, '0'),
                            "body": {"stringValue": message}
                        }]
                    }]
                }]
            }
            requests.post(self.endpoint.replace("traces", "logs"), json=payload, timeout=2)
        except Exception as e:
            import logging
            logging.debug(f"Failed to export log to OTLP: {e}")
