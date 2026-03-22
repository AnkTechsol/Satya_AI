import pytest
import os
import os
import src.satya.core.storage as storage
from src.satya.sdk.client import SatyaClient
from importlib import reload
import src.satya.auth as auth

@pytest.fixture
def temp_client(monkeypatch, tmp_path):
    monkeypatch.setenv("SATYA_AGENT_KEYS", "DEMO_KEY")
    reload(auth)

    repo_path = str(tmp_path)

    # Save original storage paths
    old_vars = {
        "SATYA_DIR": storage.SATYA_DIR,
        "TASKS_DIR": storage.TASKS_DIR,
        "TRUTH_DIR": storage.TRUTH_DIR,
        "AGENTS_DIR": storage.AGENTS_DIR,
    }

    # Mock storage paths
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    client = SatyaClient(agent_name="test_agent", repo_path=repo_path)
    yield client

    # Restore original storage paths
    for var, value in old_vars.items():
        setattr(storage, var, value)

def test_create_task_description_too_short(temp_client):
    with pytest.raises(ValueError, match="Governance Error: Task description must be at least 10 characters."):
        temp_client.create_task("Test Task", "short")

def test_create_task_description_empty(temp_client):
    with pytest.raises(ValueError, match="Governance Error: Task description must be at least 10 characters."):
        temp_client.create_task("Test Task", "")

def test_create_task_description_whitespace(temp_client):
    # Description "   12345   " stripped is "12345", length 5 < 10
    with pytest.raises(ValueError, match="Governance Error: Task description must be at least 10 characters."):
        temp_client.create_task("Test Task", "   12345   ")

def test_create_task_description_none(temp_client):
    with pytest.raises(ValueError, match="Governance Error: Task description must be at least 10 characters."):
        temp_client.create_task("Test Task", None)

def test_create_task_valid_description(temp_client):
    task = temp_client.create_task("Test Task", "This is a long enough description.")
    assert task["title"] == "Test Task"
    assert task["description"] == "This is a long enough description."
    assert task["id"] is not None
def test_poll_chat_path_traversal(monkeypatch):
    monkeypatch.setenv("SATYA_AGENT_KEY", "test_key1")
    monkeypatch.setenv("SATYA_AGENT_KEYS", "test_key1")
    import src.satya.auth as auth
    from importlib import reload
    reload(auth)

    client = SatyaClient(agent_name="../../etc/passwd")
    messages = client.poll_chat()
    assert messages == []
