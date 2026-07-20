import os
import json
import csv
from satya.sdk.adapters.csv_jsonl import CSVJSONLExporter

def test_csv_jsonl_export(tmp_path):
    export_dir = str(tmp_path / "exports")
    adapter = CSVJSONLExporter(export_dir=export_dir)

    adapter.export_trace(
        trace_id="test-trace-123",
        agent_name="test_agent",
        event_type="test_event",
        data={"key": "value"}
    )

    jsonl_path = os.path.join(export_dir, "traces.jsonl")
    csv_path = os.path.join(export_dir, "traces.csv")

    assert os.path.exists(jsonl_path)
    assert os.path.exists(csv_path)

    with open(jsonl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["trace_id"] == "test-trace-123"
        assert record["agent_name"] == "test_agent"
        assert record["event_type"] == "test_event"
        assert record["data"] == {"key": "value"}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["timestamp", "trace_id", "agent_name", "event_type", "data"]
        assert rows[1][1] == "test-trace-123"
        assert rows[1][2] == "test_agent"
        assert rows[1][3] == "test_event"
        assert json.loads(rows[1][4]) == {"key": "value"}
