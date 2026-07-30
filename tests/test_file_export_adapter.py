import os
import json
import csv
import pytest
from src.satya.sdk.adapters.file_export import JSONLExporter, CSVExporter

def test_jsonl_exporter(tmp_path):
    file_path = tmp_path / "export.jsonl"
    exporter = JSONLExporter(file_path=str(file_path))
    exporter.export_trace("trace-1", "agent-1", "test_event", {"key": "value"})
    exporter.export_log("agent-1", "test log", "task-1")
    with open(file_path, "r") as f:
        lines = f.readlines()
    assert len(lines) == 2
    trace_record = json.loads(lines[0])
    assert trace_record["type"] == "trace"
    assert trace_record["trace_id"] == "trace-1"
    assert trace_record["data"] == {"key": "value"}
    log_record = json.loads(lines[1])
    assert log_record["type"] == "log"
    assert log_record["agent_name"] == "agent-1"
    assert log_record["message"] == "test log"

def test_csv_exporter(tmp_path):
    file_path = tmp_path / "export.csv"
    exporter = CSVExporter(file_path=str(file_path))
    exporter.export_trace("trace-1", "agent-1", "test_event", {"key": "value"})
    exporter.export_log("agent-1", "test log", "task-1")
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) == 3
    assert rows[1][1] == "trace"
    assert rows[1][7] == '{"key": "value"}'
    assert rows[2][1] == "log"
    assert rows[2][3] == "agent-1"
    assert rows[2][6] == "test log"
