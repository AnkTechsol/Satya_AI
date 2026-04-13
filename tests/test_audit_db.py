import os
import sqlite3
import pytest
from src.satya.core import audit_db, storage
from src.satya.auth import append_audit_event

def test_audit_db_insertion(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET", "dummy_secret")

    repo_path = str(tmp_path)
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    db_path = audit_db.get_db_path()

    payload = {
        "timestamp": 12345.6,
        "agent_id": "test_agent",
        "task_id": "task_1",
        "trace_id": "trace_1",
        "action": "test_action",
        "details": "test details"
    }

    audit_db.insert_event(payload, "dummy_sig")

    assert os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log")
    rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0][2] == "test_agent"
    assert rows[0][6] == "test details"

    conn.close()

def test_append_audit_event_integrates_db(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET", "dummy_secret")

    repo_path = str(tmp_path)
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    sig = append_audit_event("test_agent", "task_id", "trace_id", "test_action", "details_str")

    db_path = audit_db.get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log")
    rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0][2] == "test_agent"

    conn.close()
