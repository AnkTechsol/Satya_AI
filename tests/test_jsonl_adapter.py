import sys
import os
sys.path.insert(0, "src")

import json
import pytest
from satya.sdk.adapters.jsonl_trace import JSONLAdapter

def test_export_trace(tmp_path):
    filepath = tmp_path / "traces.jsonl"
    adapter = JSONLAdapter(filepath=str(filepath))
    adapter.export_trace("test_trace", "test_agent", "test_event", {"key": "value"})

    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["trace_id"] == "test_trace"
        assert data["agent_name"] == "test_agent"
        assert data["event_type"] == "test_event"
        assert data["data"] == {"key": "value"}

def test_export_log(tmp_path):
    filepath = tmp_path / "traces.jsonl"
    adapter = JSONLAdapter(filepath=str(filepath))
    adapter.export_log("test_agent", "test_message", "test_task_id")
