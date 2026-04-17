import json
import time
import uuid
from .base import ExportAdapter
import requests

class OTLPAdapter(ExportAdapter):
    """
    OTLP Adapter to export traces and logs via OpenTelemetry HTTP JSON protocol.
    """
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or "http://localhost:4318/v1/traces"

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        try:
            now_nano = int(time.time() * 1e9)

            # Format trace_id to 32 hex chars, span_id to 16 hex chars
            formatted_trace_id = str(trace_id).replace('-', '').ljust(32, '0')[:32]
            span_id = uuid.uuid4().hex[:16]

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
                                "scope": {"name": "satya.sdk.otlp"},
                                "spans": [
                                    {
                                        "traceId": formatted_trace_id,
                                        "spanId": span_id,
                                        "name": event_type,
                                        "kind": 1,
                                        "startTimeUnixNano": str(now_nano),
                                        "endTimeUnixNano": str(now_nano),
                                        "attributes": [
                                            {"key": "event.data", "value": {"stringValue": json.dumps(data)}}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            requests.post(self.endpoint, json=payload, timeout=2)
        except Exception:
            pass

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        try:
            now_nano = int(time.time() * 1e9)

            log_endpoint = self.endpoint.replace("/v1/traces", "/v1/logs")

            payload = {
                "resourceLogs": [
                    {
                        "resource": {
                            "attributes": [
                                {"key": "service.name", "value": {"stringValue": "satya-agent"}},
                                {"key": "agent.name", "value": {"stringValue": agent_name}}
                            ]
                        },
                        "scopeLogs": [
                            {
                                "scope": {"name": "satya.sdk.otlp"},
                                "logRecords": [
                                    {
                                        "timeUnixNano": str(now_nano),
                                        "body": {"stringValue": message},
                                        "attributes": [
                                            {"key": "task.id", "value": {"stringValue": str(task_id or "")}}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            requests.post(log_endpoint, json=payload, timeout=2)
        except Exception:
            pass
