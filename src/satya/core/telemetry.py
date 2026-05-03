import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BaseExporter:
    """Base class for telemetry exporters."""
    def export(self, event_type: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError

class OTLPJsonExporter(BaseExporter):
    """Exports traces and events in a generic OpenTelemetry-like JSONL format."""

    def __init__(self, output_file: str = "otel-traces.jsonl"):
        self.output_file = output_file

    def export(self, event_type: str, data: Dict[str, Any]) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self.output_file, 'a') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to write trace: {e}")

class TelemetryManager:
    """Manages telemetry exporters and routes events."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance.exporters = []
        return cls._instance

    def add_exporter(self, exporter: BaseExporter):
        self.exporters.append(exporter)

    def track_event(self, event_type: str, data: Dict[str, Any]):
        for exporter in self.exporters:
            try:
                exporter.export(event_type, data)
            except Exception as e:
                logger.error(f"Exporter failed: {e}")

# Global instance
telemetry = TelemetryManager()
# Add default OTLP exporter
telemetry.add_exporter(OTLPJsonExporter())

def track_agent_action(agent_name: str, action: str, details: Dict[str, Any] = None):
    telemetry.track_event("agent_action", {
        "agent": agent_name,
        "action": action,
        "details": details or {}
    })

def track_task_lifecycle(task_id: str, status: str, latency_ms: Optional[float] = None):
    telemetry.track_event("task_lifecycle", {
        "task_id": task_id,
        "status": status,
        "latency_ms": latency_ms
    })
