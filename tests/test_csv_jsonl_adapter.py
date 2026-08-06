import pytest
import os
import tempfile
import json
import csv
from src.satya.sdk.adapters.csv_jsonl import CsvJsonlAdapter

def test_csv_jsonl_adapter():
    with tempfile.TemporaryDirectory() as tmpdir:
        trace_file = os.path.join(tmpdir, "traces.csv")
        log_file = os.path.join(tmpdir, "logs.jsonl")

        adapter = CsvJsonlAdapter(trace_file=trace_file, log_file=log_file)

        # Test trace
        adapter.export_trace("test-trace", "agent1", "some_event", {"key": "value"})
        assert os.path.exists(trace_file)
        with open(trace_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0] == ["timestamp", "trace_id", "agent_name", "event_type", "data"]
            assert rows[1][1] == "test-trace"
            assert rows[1][2] == "agent1"
            assert rows[1][3] == "some_event"
            assert rows[1][4] == json.dumps({"key": "value"})

        # Test log
        adapter.export_log("agent1", "a log message", "task-1")
        assert os.path.exists(log_file)
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1
            payload = json.loads(lines[0])
            assert payload["agent_name"] == "agent1"
            assert payload["message"] == "a log message"
            assert payload["task_id"] == "task-1"
            assert "timestamp" in payload
