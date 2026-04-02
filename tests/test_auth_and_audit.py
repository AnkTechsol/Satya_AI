import os
import json
import pytest
import shutil
from src.satya.auth import is_agent_authorized, is_human_authorized, sign_event, verify_event_chain, append_audit_event
from src.satya.sdk.client import SatyaClient
from src.satya.core import storage

from importlib import reload
import src.satya.auth as auth

@pytest.fixture(autouse=True)
def setup_teardown(monkeypatch, tmp_path):
    monkeypatch.setenv("SATYA_AGENT_KEYS", "test_key1,test_key2")
    monkeypatch.setenv("HUMAN_VIEW_TOKEN", "admin_secret")
    monkeypatch.setenv("AUDIT_SECRET", "test_audit_secret")

    reload(auth)

    # Mock storage to use tmp_path
    monkeypatch.setattr(storage, "SATYA_DIR", os.path.join(tmp_path, "satya_data"))
    monkeypatch.setattr(storage, "TASKS_DIR", os.path.join(tmp_path, "satya_data", "tasks"))
    monkeypatch.setattr(storage, "TRUTH_DIR", os.path.join(tmp_path, "satya_data", "truth"))
    monkeypatch.setattr(storage, "AGENTS_DIR", os.path.join(tmp_path, "satya_data", "agents"))
    storage.ensure_satya_dirs()
    yield
    # Cleanup implicitly done by tmp_path

def test_auth_checks():
    assert auth.is_agent_authorized("test_key1") is True
    assert auth.is_agent_authorized("bad_key") is False
    assert auth.is_human_authorized("admin_secret") is True
    assert auth.is_human_authorized("wrong") is False

def test_audit_event_append_and_verify():
    from src.satya.core import audit_db

    # ensure clean db for test
    db_path = audit_db.get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)

    # Append events
    sig1 = auth.append_audit_event("agent_1", "task_A", "trace_1", "task_created", "demo create")
    sig2 = auth.append_audit_event("agent_1", "task_A", "trace_1", "status_updated", "in progress", prev_hmac=sig1)

    events = audit_db.get_all_events()

    assert len(events) == 2

    assert events[0]["signature"] == sig1
    assert events[1]["signature"] == sig2

    assert auth.verify_event_chain(events) is True

def test_sdk_create_task_requires_auth(monkeypatch):
    monkeypatch.setenv("SATYA_AGENT_KEY", "invalid_key")
    with pytest.raises(PermissionError):
        client = SatyaClient(agent_name="tester")

def test_sdk_use_satya_audit_chain(monkeypatch):
    from src.satya.core import audit_db
    monkeypatch.setenv("SATYA_AGENT_KEY", "test_key1")
    client = SatyaClient(agent_name="tester")

    # ensure clean db for test
    db_path = audit_db.get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)

    # Simulate picking a task
    parent_task = client.create_task("Parent Task", "Long enough description for parent.")
    client.tasks.update_task_status(parent_task["id"], "in_progress", agent_name="tester")
    client.current_task = client.tasks.get_task(parent_task["id"])

    # Agent calls use_satya
    child_task = client.use_satya("Use satya to run a subtask", parent_trace_id=parent_task["trace_id"])

    assert child_task["parent_trace_id"] == parent_task["trace_id"]

    # Verify events
    events = audit_db.get_all_events()

    # Look for spawned_subtask
    spawn_events = [e for e in events if e["payload"]["action"] == "spawned_subtask"]
    assert len(spawn_events) == 1
    assert "child_id" in spawn_events[0]["payload"]["details"]
    assert "child_trace" in spawn_events[0]["payload"]["details"]

    # Verify the chain is valid overall
    assert auth.verify_event_chain(events) is True
