import os
import json
import csv
import tempfile
import pytest
from src.satya.sdk.adapters.csv_jsonl import CSVJSONLExportAdapter

@pytest.fixture
def temp_export_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

def test_csv_jsonl_adapter_initialization(temp_export_dir):
    adapter = CSVJSONLExportAdapter(export_dir=temp_export_dir)
    assert os.path.exists(adapter.traces_csv)
    assert os.path.exists(adapter.logs_csv)

    with open(adapter.traces_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["timestamp", "trace_id", "agent_name", "event_type", "data"]

    with open(adapter.logs_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["timestamp", "agent_name", "task_id", "message"]

def test_csv_jsonl_adapter_export_trace(temp_export_dir):
    adapter = CSVJSONLExportAdapter(export_dir=temp_export_dir)
    data = {"key": "value"}
    adapter.export_trace("trace-123", "test_agent", "test_event", data)

    # Check CSV
    with open(adapter.traces_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        row = next(reader)
        assert row[1] == "trace-123"
        assert row[2] == "test_agent"
        assert row[3] == "test_event"
        assert json.loads(row[4]) == data

    # Check JSONL
    with open(adapter.traces_jsonl, 'r', encoding='utf-8') as f:
        line = f.readline()
        record = json.loads(line)
        assert record["trace_id"] == "trace-123"
        assert record["agent_name"] == "test_agent"
        assert record["event_type"] == "test_event"
        assert record["data"] == data

def test_csv_jsonl_adapter_export_log(temp_export_dir):
    adapter = CSVJSONLExportAdapter(export_dir=temp_export_dir)
    adapter.export_log("test_agent", "Test message", "task-123")

    # Check CSV
    with open(adapter.logs_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        row = next(reader)
        assert row[1] == "test_agent"
        assert row[2] == "task-123"
        assert row[3] == "Test message"

    # Check JSONL
    with open(adapter.logs_jsonl, 'r', encoding='utf-8') as f:
        line = f.readline()
        record = json.loads(line)
        assert record["agent_name"] == "test_agent"
        assert record["task_id"] == "task-123"
        assert record["message"] == "Test message"
