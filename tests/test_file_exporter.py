import os
import json
import csv
import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.file_exporter import JSONLAdapter, CSVAdapter

def test_jsonl_adapter_export_trace(tmp_path):
    filepath = tmp_path / "traces.jsonl"
    adapter = JSONLAdapter(filepath=str(filepath))
    adapter.export_trace("trace_1", "agent_A", "event_A", {"key": "value"})

    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["trace_id"] == "trace_1"
        assert record["data"]["key"] == "value"

def test_csv_adapter_export_trace(tmp_path):
    filepath = tmp_path / "traces.csv"
    adapter = CSVAdapter(filepath=str(filepath))
    adapter.export_trace("trace_2", "agent_B", "event_B", {"key2": "value2"})

    assert os.path.exists(filepath)
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["timestamp", "trace_id", "agent_name", "event_type", "data"]
        assert rows[1][1] == "trace_2"
        assert json.loads(rows[1][4])["key2"] == "value2"
