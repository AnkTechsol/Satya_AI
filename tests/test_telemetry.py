import os
import json
import pytest
from src.satya.core.telemetry import TelemetryManager, OTLPJsonExporter, track_agent_action, track_task_lifecycle
import src.satya.core.telemetry as telemetry_module

def test_otlp_json_exporter(tmp_path):
    output_file = tmp_path / "otel-traces.jsonl"
    exporter = OTLPJsonExporter(output_file=str(output_file))

    exporter.export("test_event", {"key": "value"})

    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        lines = f.readlines()

    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["event_type"] == "test_event"
    assert data["data"]["key"] == "value"
    assert "timestamp" in data

def test_telemetry_manager():
    manager = TelemetryManager()

    class MockExporter:
        def __init__(self):
            self.events = []

        def export(self, event_type, data):
            self.events.append((event_type, data))

    mock_exporter = MockExporter()
    manager.add_exporter(mock_exporter)

    manager.track_event("test_event2", {"key": "value2"})

    assert len(mock_exporter.events) >= 1
    found = False
    for event in mock_exporter.events:
        if event[0] == "test_event2" and event[1]["key"] == "value2":
            found = True
            break
    assert found

def test_track_helpers(tmp_path):
    output_file = tmp_path / "otel-traces2.jsonl"

    manager = TelemetryManager()
    exporter = OTLPJsonExporter(output_file=str(output_file))
    manager.add_exporter(exporter)

    # Need to update global reference for helpers
    old_telemetry = telemetry_module.telemetry
    telemetry_module.telemetry = manager

    track_agent_action("TestAgent", "test_action", {"detail": "info"})
    track_task_lifecycle("task_123", "completed", latency_ms=150.0)

    # Restore
    telemetry_module.telemetry = old_telemetry

    with open(output_file, 'r') as f:
        lines = f.readlines()

    assert len(lines) == 2
    data0 = json.loads(lines[0])
    data1 = json.loads(lines[1])
    assert data0["event_type"] == "agent_action"
    assert data0["data"]["agent"] == "TestAgent"
    assert data1["event_type"] == "task_lifecycle"
    assert data1["data"]["task_id"] == "task_123"
