from .base import ExportAdapter
import datetime
import requests

class OTLPAdapter(ExportAdapter):
    """
    OTLP Adapter.
    Uses requests to send Spans to Datadog/LangSmith or any OTLP compatible endpoint.
    """
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or "http://localhost:4318/v1/traces"

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        # Mock OTLP payload matching basic OTLP structure (resourceSpans) to avoid 400 Bad Request
        payload = {
            "resourceSpans": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": agent_name}}
                    ]
                },
                "scopeSpans": [{
                    "spans": [{
                        "traceId": trace_id.encode('utf-8').hex()[:32].ljust(32, '0') if trace_id else "00000000000000000000000000000000",
                        "spanId": "0000000000000000",
                        "name": event_type,
                        "attributes": [
                            {"key": k, "value": {"stringValue": str(v)}} for k, v in data.items()
                        ]
                    }]
                }]
            }]
        }
        try:
            requests.post(self.endpoint, json=payload, timeout=2)
        except Exception as e:
            # Silent failure to avoid blocking, but standard error print could be added if needed
            print(f"[OTLPAdapter Error] Failed to export trace: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        # Mock OTLP logs payload
        payload = {
            "resourceLogs": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": agent_name}}
                    ]
                },
                "scopeLogs": [{
                    "logRecords": [{
                        "body": {"stringValue": message},
                        "attributes": [
                            {"key": "task_id", "value": {"stringValue": task_id or ""}}
                        ]
                    }]
                }]
            }]
        }
        try:
            log_endpoint = self.endpoint.replace('/v1/traces', '/v1/logs')
            requests.post(log_endpoint, json=payload, timeout=2)
        except Exception as e:
            print(f"[OTLPAdapter Error] Failed to export log: {e}")
