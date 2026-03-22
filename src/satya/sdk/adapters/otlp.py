import json
import logging
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    requests = None

from .base import ExportAdapter

logger = logging.getLogger(__name__)

class OTLPAdapter(ExportAdapter):
    """
    HTTP-based OTLP Adapter.
    Exports traces and logs to an OpenTelemetry-compatible HTTP collector.

    Expects standard OTLP/HTTP JSON structure.
    """
    def __init__(self, endpoint: str = "http://localhost:4318/v1/traces",
                 log_endpoint: str = "http://localhost:4318/v1/logs",
                 headers: Optional[Dict[str, str]] = None):
        self.endpoint = endpoint
        self.log_endpoint = log_endpoint
        self.headers = headers or {"Content-Type": "application/json"}

        if not requests:
            logger.warning("requests library not installed. OTLPAdapter will simulate exports.")

    def export_trace(self, trace_id: str, agent_name: str, event_type: str, data: dict):
        if not requests:
            logger.debug(f"Simulating OTLP Trace Export: {trace_id} by {agent_name} - {event_type}")
            return

        payload = {
            "resourceSpans": [{
                "resource": {
                    "attributes": [{"key": "service.name", "value": {"stringValue": "satya"}}]
                },
                "scopeSpans": [{
                    "scope": {"name": "satya.agent.tracer"},
                    "spans": [{
                        "traceId": trace_id.ljust(32, '0')[:32], # Ensure 32-char hex
                        "spanId": trace_id.ljust(16, '0')[:16], # Ensure 16-char hex
                        "name": f"{agent_name}.{event_type}",
                        "attributes": [
                            {"key": "agent_name", "value": {"stringValue": agent_name}},
                            {"key": "event_type", "value": {"stringValue": event_type}},
                            {"key": "data", "value": {"stringValue": json.dumps(data)}}
                        ]
                    }]
                }]
            }]
        }

        try:
            requests.post(self.endpoint, headers=self.headers, json=payload, timeout=2)
        except Exception as e:
            logger.error(f"Failed to export trace to OTLP: {e}")

    def export_log(self, agent_name: str, message: str, task_id: str = None):
        if not requests:
             logger.debug(f"Simulating OTLP Log Export: by {agent_name} on {task_id}")
             return

        payload = {
            "resourceLogs": [{
                "resource": {
                    "attributes": [{"key": "service.name", "value": {"stringValue": "satya"}}]
                },
                "scopeLogs": [{
                    "scope": {"name": "satya.agent.logger"},
                    "logRecords": [{
                        "body": {"stringValue": message},
                        "attributes": [
                            {"key": "agent_name", "value": {"stringValue": agent_name}},
                            {"key": "task_id", "value": {"stringValue": task_id or ""}}
                        ]
                    }]
                }]
            }]
        }

        try:
            requests.post(self.log_endpoint, headers=self.headers, json=payload, timeout=2)
        except Exception as e:
            logger.error(f"Failed to export log to OTLP: {e}")
