import os
import json
import csv
import pytest
from src.satya.sdk.adapters.file import CSVJSONLExportAdapter

def test_csv_export_trace(tmp_path):
    filepath = os.path.join(tmp_path, "export.csv")
    adapter = CSVJSONLExportAdapter(filepath=filepath, format="csv")

    # Trace 1
    data1 = {"key": "value"}
    adapter.export_trace("trace-1", "agent-1", "task_created", data1)

    with open(filepath, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0] == ["timestamp", "trace_id", "agent_name", "event_type", "data"]
    assert rows[1][1] == "trace-1"
    assert rows[1][2] == "agent-1"
    assert rows[1][3] == "task_created"
    assert json.loads(rows[1][4]) == data1

def test_jsonl_export_trace(tmp_path):
    filepath = os.path.join(tmp_path, "export.jsonl")
    adapter = CSVJSONLExportAdapter(filepath=filepath, format="jsonl")

    # Trace 1
    data1 = {"key": "value"}
    adapter.export_trace("trace-1", "agent-1", "task_created", data1)

    with open(filepath, "r") as f:
        lines = f.readlines()

    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["trace_id"] == "trace-1"
    assert row["agent_name"] == "agent-1"
    assert row["event_type"] == "task_created"
    assert row["data"] == data1

def test_invalid_format(tmp_path):
    filepath = os.path.join(tmp_path, "export.txt")
    with pytest.raises(ValueError):
         CSVJSONLExportAdapter(filepath=filepath, format="invalid")
