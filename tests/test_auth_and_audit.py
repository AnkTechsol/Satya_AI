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
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    events_file = os.path.join(events_dir, "audit_log.jsonl")
    if os.path.exists(events_file):
        os.remove(events_file)

    # Append events
    sig1 = auth.append_audit_event("agent_1", "task_A", "trace_1", "task_created", "demo create")
    sig2 = auth.append_audit_event("agent_1", "task_A", "trace_1", "status_updated", "in progress", prev_hmac=sig1)

    assert os.path.exists(events_file)
    with open(events_file, 'r') as f:
        lines = f.readlines()

    assert len(lines) == 2
    events = [json.loads(line) for line in lines]

    assert events[0]["signature"] == sig1
    assert events[1]["signature"] == sig2

    assert auth.verify_event_chain(events) is True

def test_audit_event_append_db(monkeypatch):
    monkeypatch.setenv("SATYA_USE_AUDIT_DB", "1")
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    db_file = os.path.join(events_dir, "audit_log.db")
    if os.path.exists(db_file):
        os.remove(db_file)

    sig1 = auth.append_audit_event("agent_1", "task_A", "trace_1", "task_created", "demo create")
    sig2 = auth.append_audit_event("agent_1", "task_A", "trace_1", "status_updated", "in progress", prev_hmac=sig1)

    assert os.path.exists(db_file)

    import sqlite3
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT signature, payload FROM audit_events ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0][0] == sig1
    assert rows[1][0] == sig2

    events = [{"signature": row[0], "payload": json.loads(row[1])} for row in rows]
    assert auth.verify_event_chain(events) is True

def test_sdk_create_task_requires_auth(monkeypatch):
    monkeypatch.setenv("SATYA_AGENT_KEY", "invalid_key")
    with pytest.raises(PermissionError):
        client = SatyaClient(agent_name="tester")

def test_sdk_use_satya_audit_chain(monkeypatch):
    monkeypatch.setenv("SATYA_AGENT_KEY", "test_key1")
    client = SatyaClient(agent_name="tester")

    events_dir = os.path.join(storage.SATYA_DIR, "events")
    events_file = os.path.join(events_dir, "audit_log.jsonl")
    if os.path.exists(events_file):
        os.remove(events_file)

    # Simulate picking a task
    parent_task = client.create_task("Parent Task", "Long enough description for parent.")
    client.tasks.update_task_status(parent_task["id"], "in_progress", agent_name="tester")
    client.current_task = client.tasks.get_task(parent_task["id"])

    # Agent calls use_satya
    child_task = client.use_satya("Use satya to run a subtask", parent_trace_id=parent_task["trace_id"])

    assert child_task["parent_trace_id"] == parent_task["trace_id"]

    # Verify events
    events_dir = os.path.join(storage.SATYA_DIR, "events")
    events_file = os.path.join(events_dir, "audit_log.jsonl")
    with open(events_file, 'r') as f:
        lines = f.readlines()

    events = [json.loads(line) for line in lines]

    # Look for spawned_subtask
    spawn_events = [e for e in events if e["payload"]["action"] == "spawned_subtask"]
    assert len(spawn_events) == 1
    assert "child_id" in spawn_events[0]["payload"]["details"]
    assert "child_trace" in spawn_events[0]["payload"]["details"]

    # Verify the chain is valid overall
    assert auth.verify_event_chain(events) is True
