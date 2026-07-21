import os
import json
import csv
from src.satya.sdk.adapters.file_export import FileExportAdapter

def test_file_export_adapter_trace(tmp_path):
    export_dir = tmp_path / "exports"
    adapter = FileExportAdapter(export_dir=str(export_dir))
    adapter.export_trace("123", "test_agent", "test_event", {"key": "value"})

    csv_path = export_dir / "traces.csv"
    assert csv_path.exists()
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[1] == ["123", "test_agent", "test_event", '{"key": "value"}']

    jsonl_path = export_dir / "traces.jsonl"
    assert jsonl_path.exists()
    with open(jsonl_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert json.loads(lines[0]) == {"trace_id": "123", "agent_name": "test_agent", "event_type": "test_event", "data": {"key": "value"}}

def test_file_export_adapter_log(tmp_path):
    export_dir = tmp_path / "exports"
    adapter = FileExportAdapter(export_dir=str(export_dir))
    adapter.export_log("test_agent", "test message", "task_123")

    csv_path = export_dir / "logs.csv"
    assert csv_path.exists()
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[1] == ["test_agent", "test message", "task_123"]

    jsonl_path = export_dir / "logs.jsonl"
    assert jsonl_path.exists()
    with open(jsonl_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert json.loads(lines[0]) == {"agent_name": "test_agent", "message": "test message", "task_id": "task_123"}
