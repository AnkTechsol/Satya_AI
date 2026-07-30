import sys
import pytest
from unittest.mock import patch, MagicMock
import os
import json

@pytest.fixture(autouse=True)
def mock_external_deps(monkeypatch):
    monkeypatch.setitem(sys.modules, 'psycopg2', MagicMock())
    monkeypatch.setitem(sys.modules, 'psycopg2.extras', MagicMock())
    monkeypatch.setitem(sys.modules, 'boto3', MagicMock())

from src.satya.core import db

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("SATYA_POSTGRES_URI", "postgresql://user:pass@localhost/testdb")
    monkeypatch.setenv("SATYA_S3_BUCKET", "test-bucket")
    monkeypatch.setenv("SATYA_SQLITE_DB", "test_audit.db")

@patch("src.satya.core.db.boto3")
@patch("src.satya.core.db.psycopg2")
def test_append_event_to_postgres_s3(mock_psycopg2, mock_boto3, mock_env):
    mock_s3_client = MagicMock()
    mock_boto3.client.return_value = mock_s3_client

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    event = {
        "payload": {
            "timestamp": 12345.0,
            "agent_id": "test_agent",
            "task_id": "task_1",
            "trace_id": "trace_1",
            "action": "test_action",
            "details": {"key": "value"}
        },
        "signature": "test_signature"
    }

    # Reset globals in db to allow testing
    db._DB_INITIALIZED = False
    db._PG_INITIALIZED = False

    db.append_event_to_db(event)

    # Check S3 upload
    mock_boto3.client.assert_called_with("s3")
    mock_s3_client.put_object.assert_called_once()

    put_kwargs = mock_s3_client.put_object.call_args[1]
    assert put_kwargs["Bucket"] == "test-bucket"
    assert "audit_events/" in put_kwargs["Key"]
    assert json.loads(put_kwargs["Body"]) == event

    # Check Postgres initialization
    mock_psycopg2.connect.assert_called_with("postgresql://user:pass@localhost/testdb")

    # Check Postgres insertion
    mock_cursor.execute.assert_called()
    insert_call = [call for call in mock_cursor.execute.call_args_list if "INSERT INTO audit_log" in call[0][0]][0]

    args = insert_call[0][1]
    assert args[0] == 12345.0
    assert args[1] == "test_agent"
    assert args[2] == "task_1"
    assert args[3] == "trace_1"
    assert args[4] == "test_action"
    assert args[5] == '{"key": "value"}'
    assert args[6] == "test_signature"
    assert args[7].startswith("s3://test-bucket/audit_events/")

    mock_conn.commit.assert_called()

def test_s3_upload_no_bucket():
    assert db.upload_to_s3({}) == ""
