import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# To use this durable store, set:
# SATYA_POSTGRES_DB_URI (e.g. postgresql://user:pass@host/db)
# SATYA_S3_BUCKET (e.g. my-satya-audits)
# (Optional) SATYA_AWS_ACCESS_KEY_ID, SATYA_AWS_SECRET_ACCESS_KEY, SATYA_AWS_REGION

_POSTGRES_INITIALIZED = False

def _get_postgres_uri() -> str:
    return os.environ.get("SATYA_POSTGRES_DB_URI", "")

def _get_s3_bucket() -> str:
    return os.environ.get("SATYA_S3_BUCKET", "")

def init_postgres():
    """Initialize the Postgres DB schema if it doesn't exist."""
    global _POSTGRES_INITIALIZED
    if _POSTGRES_INITIALIZED:
        return

    uri = _get_postgres_uri()
    if not uri:
        return

    try:
        import psycopg2
        with psycopg2.connect(uri) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS satya_audit_log (
                        id SERIAL PRIMARY KEY,
                        timestamp DOUBLE PRECISION NOT NULL,
                        agent_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        trace_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        details TEXT NOT NULL,
                        signature TEXT NOT NULL,
                        s3_pointer TEXT
                    )
                ''')
            conn.commit()
        _POSTGRES_INITIALIZED = True
    except ImportError:
        logger.warning("psycopg2 not installed. Cannot use Postgres durable audit store.")
    except Exception as e:
        logger.error(f"Failed to initialize Postgres DB: {e}")

def _upload_to_s3(event: Dict[str, Any], event_id: str) -> str:
    """Upload full event to S3 as JSON and return the pointer (S3 URI)."""
    bucket = _get_s3_bucket()
    if not bucket:
        return ""

    try:
        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get("SATYA_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("SATYA_AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("SATYA_AWS_REGION")
        )
        object_key = f"audits/{event_id}.json"
        s3.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=json.dumps(event).encode('utf-8'),
            ContentType='application/json'
        )
        return f"s3://{bucket}/{object_key}"
    except ImportError:
        logger.warning("boto3 not installed. Cannot upload to S3.")
        return ""
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        return ""

def append_event_to_db(event: Dict[str, Any]):
    """Append a signed audit event to Postgres + S3."""
    uri = _get_postgres_uri()
    if not uri:
        return

    init_postgres()

    payload = event.get("payload", {})
    signature = str(event.get("signature", ""))

    timestamp = payload.get("timestamp", 0.0)
    agent_id = str(payload.get("agent_id", ""))
    task_id = str(payload.get("task_id", ""))
    trace_id = str(payload.get("trace_id", ""))
    action = str(payload.get("action", ""))

    details = payload.get("details", "")
    if isinstance(details, dict):
        details_str = json.dumps(details)
    elif not isinstance(details, str):
        details_str = str(details)
    else:
        details_str = details

    # Optional S3 offload for full payload
    event_id = f"{timestamp}_{agent_id}_{trace_id}".replace(".", "_")
    s3_pointer = _upload_to_s3(event, event_id)

    try:
        import psycopg2
        with psycopg2.connect(uri) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO satya_audit_log (timestamp, agent_id, task_id, trace_id, action, details, signature, s3_pointer)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    timestamp, agent_id, task_id, trace_id, action, details_str, signature, s3_pointer
                ))
            conn.commit()
    except Exception as e:
        logger.error(f"Postgres DB Error while appending event: {e}")
