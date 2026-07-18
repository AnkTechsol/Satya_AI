import os
import json
import pytest
from src.satya.core.export import export_tasks_to_jsonl
from src.satya.core import storage

from src.satya.core.export import export_tasks_to_jsonl, export_tasks_to_csv
import csv

def test_export_tasks_to_jsonl(tmp_path, monkeypatch):
    tasks_dir = str(tmp_path / "tasks")
    monkeypatch.setattr(storage, 'TASKS_DIR', tasks_dir)
    os.makedirs(tasks_dir, exist_ok=True)

    task1 = {"id": "t1", "title": "Task 1"}
    task2 = {"id": "t2", "title": "Task 2"}

    with open(os.path.join(tasks_dir, "t1.json"), "w") as f:
        json.dump(task1, f)
    with open(os.path.join(tasks_dir, "t2.json"), "w") as f:
        json.dump(task2, f)

    output_file = str(tmp_path / "output.jsonl")
    count = export_tasks_to_jsonl(output_file)

    assert count == 2
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 2
        data = [json.loads(line) for line in lines]
        assert any(d["id"] == "t1" for d in data)
        assert any(d["id"] == "t2" for d in data)

def test_export_tasks_no_parent_dir_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tasks_dir = "tasks"
    monkeypatch.setattr(storage, 'TASKS_DIR', tasks_dir)
    os.makedirs(tasks_dir, exist_ok=True)
    output_file = "pure_filename_output.jsonl"
    count = export_tasks_to_jsonl(output_file)
    assert os.path.exists(output_file)

def test_export_tasks_to_csv(tmp_path, monkeypatch):
    tasks_dir = str(tmp_path / "tasks")
    monkeypatch.setattr(storage, 'TASKS_DIR', tasks_dir)
    os.makedirs(tasks_dir, exist_ok=True)

    task1 = {"id": "t1", "title": "Task 1", "metadata": {"key": "value"}}
    task2 = {"id": "t2", "title": "Task 2", "status": "done"}

    with open(os.path.join(tasks_dir, "t1.json"), "w") as f:
        json.dump(task1, f)
    with open(os.path.join(tasks_dir, "t2.json"), "w") as f:
        json.dump(task2, f)

    output_file = str(tmp_path / "output.csv")
    count = export_tasks_to_csv(output_file)

    assert count == 2
    assert os.path.exists(output_file)

    with open(output_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 2
        assert set(reader.fieldnames) == {"id", "title", "metadata", "status"}
        assert reader.fieldnames[0] == "id"

        # Verify JSON serialization of nested fields
        t1_row = next(r for r in rows if r["id"] == "t1")
        assert t1_row["title"] == "Task 1"
        assert t1_row["metadata"] == '{"key": "value"}'
        assert t1_row["status"] == ""

        t2_row = next(r for r in rows if r["id"] == "t2")
        assert t2_row["title"] == "Task 2"
        assert t2_row["metadata"] == ""
        assert t2_row["status"] == "done"
