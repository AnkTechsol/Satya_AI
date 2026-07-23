import os
import json
import csv
from src.satya.sdk.adapters.csv_jsonl import CSVJSONLAdapter

def test_csv_jsonl_adapter(tmp_path):
    export_dir = str(tmp_path / "exports")
    adapter = CSVJSONLAdapter(export_dir=export_dir)

    # Test trace
    adapter.export_trace("trace123", "agentA", "task_created", {"key": "val"})

    assert os.path.exists(os.path.join(export_dir, "traces.csv"))
    assert os.path.exists(os.path.join(export_dir, "traces.jsonl"))

    with open(os.path.join(export_dir, "traces.jsonl")) as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["trace_id"] == "trace123"
        assert json.loads(data["data"]) == {"key": "val"}

    with open(os.path.join(export_dir, "traces.csv")) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["trace_id"] == "trace123"

    # Test log
    adapter.export_log("agentA", "hello", "task1")

    assert os.path.exists(os.path.join(export_dir, "logs.csv"))
    assert os.path.exists(os.path.join(export_dir, "logs.jsonl"))

    with open(os.path.join(export_dir, "logs.jsonl")) as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["message"] == "hello"

    with open(os.path.join(export_dir, "logs.csv")) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["message"] == "hello"
