import os
import sqlite3
import pytest
import shutil
import time

from src.satya.core import audit_db
from src.satya.core import storage

@pytest.fixture
def clean_db():
    storage.ensure_satya_dirs()
    db_path = audit_db.get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
    yield
    if os.path.exists(db_path):
        os.remove(db_path)

def test_audit_db_append_and_get(clean_db):
    event1 = {
        "payload": {
            "timestamp": time.time(),
            "agent_id": "agent1",
            "task_id": "task1",
            "trace_id": "trace1",
            "action": "action1",
            "details": "details1"
        }
    }
    signature1 = "sig1"

    assert audit_db.append_event(event1, signature1)

    event2 = {
        "payload": {
            "timestamp": time.time(),
            "agent_id": "agent2",
            "task_id": "task2",
            "trace_id": "trace2",
            "action": "action2",
            "details": "details2"
        }
    }
    signature2 = "sig2"

    assert audit_db.append_event(event2, signature2)

    assert audit_db.get_last_signature() == signature2

    events = audit_db.get_all_events()
    assert len(events) == 2
    assert events[0]["signature"] == signature1
    assert events[0]["payload"]["agent_id"] == "agent1"
    assert events[1]["signature"] == signature2
    assert events[1]["payload"]["agent_id"] == "agent2"

def test_audit_db_empty(clean_db):
    assert audit_db.get_last_signature() == ""
    assert audit_db.get_all_events() == []
