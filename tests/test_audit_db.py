import os
import tempfile
import pytest
import json
from src.satya.core.audit_db import AuditDB

@pytest.fixture
def temp_db(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr('src.satya.core.storage.SATYA_DIR', tmpdir)
        monkeypatch.setattr('src.satya.core.storage.ensure_satya_dirs', lambda: os.makedirs(os.path.join(tmpdir, "events"), exist_ok=True))
        yield AuditDB()

def test_audit_db_init(temp_db):
    assert os.path.exists(temp_db.db_path)

def test_audit_db_append_and_get(temp_db):
    test_event = {
        "payload": {
            "timestamp": 123456789.0,
            "agent_id": "test_agent",
            "task_id": "task_1",
            "trace_id": "trace_1",
            "action": "test_action",
            "details": "test details"
        },
        "signature": "test_signature"
    }

    assert temp_db.append_event(test_event) == True

    events = temp_db.get_all_events()
    assert len(events) == 1

    retrieved_event = events[0]
    assert retrieved_event["signature"] == "test_signature"
    assert retrieved_event["payload"]["agent_id"] == "test_agent"
    assert retrieved_event["payload"]["action"] == "test_action"

def test_audit_db_empty(temp_db):
    events = temp_db.get_all_events()
    assert len(events) == 0
