import os
import json
import pytest
from src.satya.core.tasks import Tasks, STATUS_IN_PROGRESS, STATUS_DONE
import src.satya.core.telemetry as telemetry_module
from src.satya.core.telemetry import TelemetryManager, OTLPJsonExporter

def test_tasks_with_telemetry(tmp_path):
    repo_path = str(tmp_path)
    os.makedirs(os.path.join(repo_path, ".git"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, "satya_data", "tasks"), exist_ok=True)

    # Write a dummy completion criteria file to avoid CompletionCriteriaNotMet
    os.makedirs(os.path.join(repo_path, "tests"), exist_ok=True)
    with open(os.path.join(repo_path, "tests", "test_dummy.py"), "w") as f:
        f.write("def test_dummy(): pass")

    output_file = tmp_path / "otel-traces.jsonl"

    # Set up isolated telemetry manager
    TelemetryManager._instance = None
    manager = TelemetryManager()
    exporter = OTLPJsonExporter(output_file=str(output_file))
    manager.add_exporter(exporter)

    old_telemetry = telemetry_module.telemetry
    telemetry_module.telemetry = manager

    try:
        tasks = Tasks(repo_path=repo_path)

        # We need a manual mock for commit_and_push to avoid git errors in testing
        tasks.git_handler.commit_and_push = lambda files, msg: True

        task = tasks.create_task("Test Task", "Desc")
        assert task is not None
        task_id = task["id"]

        # Move to progress
        tasks.update_task_status(task_id, STATUS_IN_PROGRESS)

        # Verify trace JSON has our events
        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 2
        data0 = json.loads(lines[0])
        data1 = json.loads(lines[1])
        assert data0["event_type"] == "task_lifecycle"
        assert data0["data"]["task_id"] == task_id
        assert data0["data"]["status"] == "queued"

        assert data1["event_type"] == "task_lifecycle"
        assert data1["data"]["status"] == "in_progress"

    finally:
        telemetry_module.telemetry = old_telemetry
