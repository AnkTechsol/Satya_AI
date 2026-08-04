import os
import json
import csv
import tempfile
from satya.sdk.adapters.file import FileAdapter

def test_file_adapter_export_trace():
    with tempfile.TemporaryDirectory() as temp_dir:
        adapter = FileAdapter(output_dir=temp_dir)
        adapter.export_trace("trace123", "agentA", "test_event", {"key": "value"})

        with open(adapter.traces_jsonl, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1
            record = json.loads(lines[0])
            assert record["trace_id"] == "trace123"
            assert record["agent_name"] == "agentA"
            assert record["event_type"] == "test_event"
            assert record["data"] == {"key": "value"}

        with open(adapter.traces_csv, "r", newline="", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            assert len(reader) == 2
            assert reader[1][1] == "trace123"
            assert reader[1][2] == "agentA"
            assert reader[1][3] == "test_event"
            assert json.loads(reader[1][4]) == {"key": "value"}

def test_file_adapter_export_log():
    with tempfile.TemporaryDirectory() as temp_dir:
        adapter = FileAdapter(output_dir=temp_dir)
        adapter.export_log("agentB", "test message", "task456")

        with open(adapter.logs_jsonl, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1
            record = json.loads(lines[0])
            assert record["agent_name"] == "agentB"
            assert record["message"] == "test message"
            assert record["task_id"] == "task456"
