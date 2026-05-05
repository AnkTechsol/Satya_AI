import os
import json
from unittest.mock import patch, MagicMock
from src.satya.core import db_postgres

import sys

# Pre-mock so db_postgres can import them
sys.modules['boto3'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()

@patch.dict(os.environ, {
    "SATYA_POSTGRES_DB_URI": "postgresql://user:pass@localhost/db",
    "SATYA_S3_BUCKET": "test-bucket",
    "SATYA_AWS_ACCESS_KEY_ID": "test-key",
    "SATYA_AWS_SECRET_ACCESS_KEY": "test-secret",
    "SATYA_AWS_REGION": "us-east-1"
})
def test_postgres_append_event():
    import boto3
    import psycopg2

    mock_boto3 = boto3
    mock_psycopg2 = psycopg2

    # Reset initialization state for testing
    db_postgres._POSTGRES_INITIALIZED = False

    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_psycopg2.connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock S3 client
    mock_s3 = MagicMock()
    mock_boto3.client.return_value = mock_s3

    event = {
        "payload": {
            "timestamp": 1234567890.0,
            "agent_id": "agent-1",
            "task_id": "task-1",
            "trace_id": "trace-1",
            "action": "create",
            "details": {"key": "value"}
        },
        "signature": "test-signature"
    }

    db_postgres.append_event_to_db(event)

    # Verify S3 upload
    mock_boto3.client.assert_called_once_with(
        's3',
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        region_name="us-east-1"
    )
    mock_s3.put_object.assert_called_once()
    call_args = mock_s3.put_object.call_args[1]
    assert call_args['Bucket'] == "test-bucket"
    assert "1234567890_0_agent-1_trace-1.json" in call_args['Key']
    assert call_args['ContentType'] == 'application/json'

    # Verify Postgres initialization and insert
    assert mock_psycopg2.connect.call_count == 2  # Once for init, once for insert

    assert mock_cursor.execute.call_count == 2

    # Check the insert call
    insert_call = mock_cursor.execute.call_args_list[1]
    query, params = insert_call[0]

    assert "INSERT INTO satya_audit_log" in query
    assert params[0] == 1234567890.0
    assert params[1] == "agent-1"
    assert params[2] == "task-1"
    assert params[3] == "trace-1"
    assert params[4] == "create"
    assert params[5] == json.dumps({"key": "value"})
    assert params[6] == "test-signature"
    assert "s3://test-bucket/audits/" in params[7]
