import os
import json
import pytest
from datetime import datetime, timezone, timedelta

from src.satya.core.project_manager import Orchestrator
from src.satya.core.tasks import Tasks, STATUS_QUEUED, STATUS_IN_PROGRESS

@pytest.fixture
def temp_satya_dirs(tmp_path, monkeypatch):
    """
    Mock storage directories to run tests in isolation.
    """
    satya_dir = tmp_path / "satya_data"
    tasks_dir = satya_dir / "tasks"
    truth_dir = satya_dir / "truth"
    agents_dir = satya_dir / "agents"
    heartbeats_dir = satya_dir / "heartbeats"

    monkeypatch.setattr("src.satya.core.storage.SATYA_DIR", str(satya_dir))
    monkeypatch.setattr("src.satya.core.storage.TASKS_DIR", str(tasks_dir))
    monkeypatch.setattr("src.satya.core.storage.TRUTH_DIR", str(truth_dir))
    monkeypatch.setattr("src.satya.core.storage.AGENTS_DIR", str(agents_dir))
    monkeypatch.setattr("src.satya.core.storage.HEARTBEATS_DIR", str(heartbeats_dir))

    import src.satya.core.storage as storage
    storage.ensure_satya_dirs()
    return satya_dir

def test_record_heartbeat(temp_satya_dirs):
    orchestrator = Orchestrator(repo_path=str(temp_satya_dirs))
    agent_name = "test_agent"

    # Record heartbeat
    assert orchestrator.record_heartbeat(agent_name) is True

    # Verify file exists and has valid timestamp
    heartbeat_path = temp_satya_dirs / "heartbeats" / f"{agent_name}.json"
    assert heartbeat_path.exists()

    with open(heartbeat_path, "r") as f:
        data = json.load(f)

    assert data["agent"] == agent_name
    assert "last_heartbeat" in data

def test_check_heartbeats_recovers_task(temp_satya_dirs):
    orchestrator = Orchestrator(repo_path=str(temp_satya_dirs), timeout_minutes=5)
    tasks = Tasks(repo_path=str(temp_satya_dirs))

    # Create a task and put it in progress
    task = tasks.create_task("Test Task", "This is a test task for recovery")
    task_id = task["id"]
    agent_name = "dead_agent"

    tasks.update_task_status(task_id, STATUS_IN_PROGRESS, agent_name=agent_name)

    # Manually lock task to the agent
    tasks.lock_task(task_id, agent_name)

    # Simulate an old heartbeat (e.g. 10 minutes ago)
    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    heartbeat_data = {
        "agent": agent_name,
        "last_heartbeat": past_time.isoformat().replace("+00:00", "") + "Z"
    }

    heartbeat_path = temp_satya_dirs / "heartbeats" / f"{agent_name}.json"
    with open(heartbeat_path, "w") as f:
        json.dump(heartbeat_data, f)

    # Run Orchestrator check
    recovered = orchestrator.check_heartbeats(run_once=True)

    assert len(recovered) == 1
    recovered_task = recovered[0]
    assert recovered_task["id"] == task_id
    assert recovered_task["status"] == STATUS_QUEUED
    assert recovered_task["locked_by"] is None

    # Verify audit trail
    audit_trail = recovered_task.get("audit_trail", [])
    assert audit_trail[-1]["action"] == "Task Recovered"

def test_check_heartbeats_ignores_healthy_agent(temp_satya_dirs):
    orchestrator = Orchestrator(repo_path=str(temp_satya_dirs), timeout_minutes=5)
    tasks = Tasks(repo_path=str(temp_satya_dirs))

    # Create a task and put it in progress
    task = tasks.create_task("Test Task", "This is a test task for healthy agent")
    task_id = task["id"]
    agent_name = "healthy_agent"

    tasks.update_task_status(task_id, STATUS_IN_PROGRESS, agent_name=agent_name)
    tasks.lock_task(task_id, agent_name)

    # Record a fresh heartbeat
    orchestrator.record_heartbeat(agent_name)

    # Force a delay in test to ensure times differ or just set explicit times to avoid fast execution bugs.
    # For a deterministic test, we should explicitly update the locked_at to be *now* as well.
    current_task = tasks.get_task(task_id)
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "") + "Z"
    current_task["locked_at"] = now_iso
    filepath = temp_satya_dirs / "tasks" / f"{task_id}.json"
    with open(filepath, 'w') as f:
        json.dump(current_task, f)

    heartbeat_path = temp_satya_dirs / "heartbeats" / f"{agent_name}.json"
    assert heartbeat_path.exists()

    # Run Orchestrator check
    recovered = orchestrator.check_heartbeats(run_once=True)

    # Task should not be recovered
    assert len(recovered) == 0

    # Verify task is still in progress
    current_task = tasks.get_task(task_id)
    assert current_task["status"] == STATUS_IN_PROGRESS
    assert current_task["locked_by"] == agent_name
