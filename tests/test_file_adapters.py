import os
import json
import csv
from satya.sdk.adapters.file import CSVExportAdapter, JSONLExportAdapter

def test_csv_export_adapter(tmp_path):
    filepath = str(tmp_path / "traces.csv")
    adapter = CSVExportAdapter(filepath=filepath)

    adapter.export_trace(
        trace_id="123",
        agent_name="test_agent",
        event_type="test_event",
        data={"key": "value"}
    )

    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["timestamp", "trace_id", "agent_name", "event_type", "data"]
        assert rows[1][1] == "123"
        assert rows[1][2] == "test_agent"
        assert rows[1][3] == "test_event"
        assert json.loads(rows[1][4]) == {"key": "value"}

    adapter.export_log("test_agent", "log msg", "task_1")

def test_jsonl_export_adapter(tmp_path):
    filepath = str(tmp_path / "traces.jsonl")
    adapter = JSONLExportAdapter(filepath=filepath)

    adapter.export_trace(
        trace_id="456",
        agent_name="test_agent",
        event_type="test_event",
        data={"key": "value"}
    )

    adapter.export_log("test_agent", "log msg", "task_1")

    with open(filepath, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2
        trace_event = json.loads(lines[0])
        assert trace_event["trace_id"] == "456"
        assert trace_event["agent_name"] == "test_agent"

        log_event = json.loads(lines[1])
        assert log_event["message"] == "log msg"
        assert log_event["task_id"] == "task_1"
