import os
import json
import csv
from src.satya.sdk.adapters.file_exporter import FileExportAdapter

def test_file_export_adapter(tmp_path):
    traces_file = str(tmp_path / "traces.jsonl")
    logs_file = str(tmp_path / "logs.csv")

    adapter = FileExportAdapter(traces_filepath=traces_file, logs_filepath=logs_file)
    adapter.export_trace("trace-1", "agent-1", "task_created", {"key": "value"})
    adapter.export_log("agent-1", "test log", "task-1")

    assert os.path.exists(traces_file)
    assert os.path.exists(logs_file)

    with open(traces_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["trace_id"] == "trace-1"
        assert record["data"] == {"key": "value"}

    with open(logs_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2 # header + data
        assert rows[1][1] == "agent-1"
        assert rows[1][2] == "task-1"
        assert rows[1][3] == "test log"
