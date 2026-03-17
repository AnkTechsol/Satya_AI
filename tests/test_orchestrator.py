import os
import shutil
import pytest
import time
from datetime import datetime, timezone, timedelta
from src.satya.core.tasks import Tasks, STATUS_IN_PROGRESS, STATUS_QUEUED
import src.satya.core.storage as storage
from project_manager import start_orchestrator
import threading

@pytest.fixture
def temp_orchestrator():
    repo_path = "test_repo_orchestrator"
    os.makedirs(repo_path, exist_ok=True)

    old_dir = storage.SATYA_DIR
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")
    storage.HEARTBEATS_DIR = os.path.join(storage.SATYA_DIR, "heartbeats")

    storage.ensure_satya_dirs()

    tasks_mgr = Tasks(repo_path)

    yield tasks_mgr, repo_path

    shutil.rmtree(repo_path)
    storage.SATYA_DIR = old_dir
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")
    storage.HEARTBEATS_DIR = os.path.join(storage.SATYA_DIR, "heartbeats")

def test_heartbeat_saving(temp_orchestrator):
    tasks_mgr, _ = temp_orchestrator

    now = datetime.now(timezone.utc).isoformat() + "Z"
    hb_data = {
        "last_seen": now,
        "status": "online",
        "agent_name": "agent1",
        "current_task_id": "123"
    }

    assert storage.save_heartbeat("agent1", hb_data) is True

    hbs = storage.get_heartbeats()
    assert "agent1" in hbs
    assert hbs["agent1"]["status"] == "online"

def test_orchestrator_reassigns_dead_agent_task(temp_orchestrator):
    tasks_mgr, repo_path = temp_orchestrator

    # 1. Create a task and assign it to an agent
    task = tasks_mgr.create_task("Test Task", "Description")
    tasks_mgr.update_task_status(task["id"], STATUS_IN_PROGRESS, "agent_dead")
    tasks_mgr.update_task(task["id"], {"assignee": "agent_dead"})

    # 2. Simulate agent sending a heartbeat a long time ago (10 minutes ago)
    old_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    hb_data = {
        "last_seen": old_time.isoformat() + "Z",
        "status": "online",
        "agent_name": "agent_dead",
        "current_task_id": task["id"]
    }
    storage.save_heartbeat("agent_dead", hb_data)

    # 3. Run the orchestrator logic manually
    start_orchestrator(repo_path, timeout_minutes=5, poll_interval=1, run_once=True)

    # 4. Check if task was re-queued
    updated_task = tasks_mgr.get_task(task["id"])
    assert updated_task["status"] == STATUS_QUEUED
    assert updated_task["assignee"] == "Unassigned"

    # Check if agent was marked offline
    hbs = storage.get_heartbeats()
    assert hbs["agent_dead"]["status"] == "offline"

def test_orchestrator_ignores_alive_agent(temp_orchestrator):
    tasks_mgr, repo_path = temp_orchestrator

    task = tasks_mgr.create_task("Test Task 2", "Description")
    tasks_mgr.update_task_status(task["id"], STATUS_IN_PROGRESS, "agent_alive")
    tasks_mgr.update_task(task["id"], {"assignee": "agent_alive"})

    # 2. Simulate agent sending a heartbeat just now
    now = datetime.now(timezone.utc)
    hb_data = {
        "last_seen": now.isoformat() + "Z",
        "status": "online",
        "agent_name": "agent_alive",
        "current_task_id": task["id"]
    }
    storage.save_heartbeat("agent_alive", hb_data)

    # 3. Run the orchestrator logic
    start_orchestrator(repo_path, timeout_minutes=5, poll_interval=1, run_once=True)

    # 4. Check that task is still In Progress
    updated_task = tasks_mgr.get_task(task["id"])
    assert updated_task["status"] == STATUS_IN_PROGRESS
    assert updated_task["assignee"] == "agent_alive"
