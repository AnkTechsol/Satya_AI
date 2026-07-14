import os
import json
import pytest
from src.satya.sdk.adapters.file import FileExportAdapter

def test_file_export_adapter_trace(tmp_path):
    filepath = os.path.join(tmp_path, "test_traces.jsonl")
    adapter = FileExportAdapter(filepath)

    adapter.export_trace("trace-1", "test_agent", "start", {"key": "value"})

    with open(filepath, "r") as f:
        data = json.loads(f.read().strip())

    assert data["trace_id"] == "trace-1"
    assert data["agent_name"] == "test_agent"
    assert data["event_type"] == "start"
    assert data["data"] == {"key": "value"}

def test_file_export_adapter_log(tmp_path):
    filepath = os.path.join(tmp_path, "test_traces.jsonl")
    adapter = FileExportAdapter(filepath)

    adapter.export_log("test_agent", "doing work", "task-1")

    with open(filepath, "r") as f:
        data = json.loads(f.read().strip())

    assert data["type"] == "log"
    assert data["agent_name"] == "test_agent"
    assert data["message"] == "doing work"
    assert data["task_id"] == "task-1"

def test_file_export_adapter_pure_filename():
    # Should not raise exception
    adapter = FileExportAdapter("pure_filename.jsonl")
    assert adapter.filepath == "pure_filename.jsonl"
    if os.path.exists("pure_filename.jsonl"):
        os.remove("pure_filename.jsonl")
