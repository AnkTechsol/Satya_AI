import os
import shutil
import pytest
import src.satya.sdk as satya
from importlib import reload
import src.satya.auth as auth

@pytest.fixture
def test_client(monkeypatch):
    monkeypatch.setenv("SATYA_AGENT_KEYS", "DEMO_KEY")
    reload(auth)
    repo_path = "test_repo"
    os.makedirs(repo_path, exist_ok=True)

    import src.satya.core.storage as storage
    old_dir = storage.SATYA_DIR
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    client = satya.init(agent_name="test_agent", repo_path=repo_path)
    yield client

    shutil.rmtree(repo_path)
    storage.SATYA_DIR = old_dir
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

def test_allowed_action_returns_true(test_client):
    task = test_client.create_task("Test", "Long enough desc")
    test_client.tasks.update_task(task["id"], {"allowed_actions": ["read_file", "write_file"]}, "agent")

    assert test_client.can_do("read_file", task["id"]) == True

def test_forbidden_action_returns_false(test_client):
    task = test_client.create_task("Test", "Long enough desc")
    test_client.tasks.update_task(task["id"], {
        "allowed_actions": ["write_file"],
        "forbidden_actions": ["write_file"]
    }, "agent")

    assert test_client.can_do("write_file", task["id"]) == False

def test_unlisted_action_returns_false(test_client):
    task = test_client.create_task("Test", "Long enough desc")
    test_client.tasks.update_task(task["id"], {"allowed_actions": ["read_file"]}, "agent")

    assert test_client.can_do("delete_file", task["id"]) == False

def test_blocked_action_is_logged(test_client):
    task = test_client.create_task("Test", "Long enough desc")
    task_id = task["id"]
    test_client.tasks.update_task(task_id, {"allowed_actions": []}, "agent")

    # Read log file before
    log_path = test_client.log_path

    assert test_client.can_do("delete_file", task_id) == False

    with open(log_path, 'r') as f:
        content = f.read()

    assert f"BLOCKED: 'delete_file' not permitted for task {task_id}" in content
