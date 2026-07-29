import os
import json
import csv
from src.satya.sdk.adapters.csv_jsonl import CsvJsonlAdapter

def test_csv_jsonl_adapter_export(tmp_path):
    adapter = CsvJsonlAdapter(str(tmp_path))
    adapter.export_trace("trace123", "agentA", "test_event", {"key": "value"})

    assert os.path.exists(adapter.csv_path)
    assert os.path.exists(adapter.jsonl_path)

    with open(adapter.csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 2
        assert reader[0] == ["trace_id", "agent_name", "event_type", "timestamp", "data"]
        assert reader[1][0] == "trace123"
        assert reader[1][1] == "agentA"
        assert reader[1][2] == "test_event"
        assert json.loads(reader[1][4]) == {"key": "value"}

    with open(adapter.jsonl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["trace_id"] == "trace123"
        assert record["agent_name"] == "agentA"
        assert record["event_type"] == "test_event"
        assert record["data"] == {"key": "value"}
