import pytest
import os
import json
from satya.sdk.adapters.jsonl import OTLPJsonExporter

def test_jsonl_export_trace(tmp_path):
    filepath = tmp_path / "test.jsonl"
    adapter = OTLPJsonExporter(filepath=str(filepath))
    adapter.export_trace("trace-1", "agent-1", "task_created", {"data": "test"})

    with open(filepath, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["trace_id"] == "trace-1"
        assert record["event_type"] == "task_created"

def test_jsonl_export_log(tmp_path):
    filepath = tmp_path / "test.jsonl"
    adapter = OTLPJsonExporter(filepath=str(filepath))
    adapter.export_log("agent-1", "test log", "task-1")

    with open(filepath, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["message"] == "test log"
        assert record["task_id"] == "task-1"