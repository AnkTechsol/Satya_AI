import os
import sqlite3
import json
import logging
import uuid
from typing import Dict, Any

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    psycopg2 = None

try:
    import boto3
except ImportError:
    boto3 = None

logger = logging.getLogger(__name__)

_DB_INITIALIZED = False
_PG_INITIALIZED = False

def get_db_path() -> str:
    """Return the path to the SQLite DB if configured, else empty string."""
    return os.environ.get("SATYA_SQLITE_DB", "")

def get_pg_uri() -> str:
    """Return the path to the Postgres DB if configured, else empty string."""
    return os.environ.get("SATYA_POSTGRES_URI", "")

def get_s3_bucket() -> str:
    """Return the S3 bucket if configured, else empty string."""
    return os.environ.get("SATYA_S3_BUCKET", "")

def upload_to_s3(event: Dict[str, Any]) -> str:
    bucket = get_s3_bucket()
    if not bucket or not boto3:
        return ""
    try:
        s3 = boto3.client("s3")
        key = f"audit_events/{uuid.uuid4()}.json"
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(event),
            ContentType="application/json"
        )
        return f"s3://{bucket}/{key}"
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        return ""

def init_db():
    """Initialize DB schema if it doesn't exist."""
    global _DB_INITIALIZED, _PG_INITIALIZED

    pg_uri = get_pg_uri()
    if pg_uri and psycopg2 and not _PG_INITIALIZED:
        try:
            conn = psycopg2.connect(pg_uri)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    timestamp DOUBLE PRECISION NOT NULL,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    s3_uri TEXT
                )
            ''')
            conn.commit()
            conn.close()
            _PG_INITIALIZED = True
        except Exception as e:
            logger.error(f"Failed to initialize Postgres DB: {e}")

    db_path = get_db_path()
    if db_path and not _DB_INITIALIZED:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    signature TEXT NOT NULL
                )
            ''')

            # Migration logic for adding s3_uri to existing sqlite databases
            cursor.execute("PRAGMA table_info(audit_log)")
            columns = [col[1] for col in cursor.fetchall()]
            if 's3_uri' not in columns:
                cursor.execute("ALTER TABLE audit_log ADD COLUMN s3_uri TEXT")

            conn.commit()
            conn.close()
            _DB_INITIALIZED = True
        except Exception as e:
            logger.error(f"Failed to initialize SQLite DB: {e}")

def append_event_to_db(event: Dict[str, Any]):
    """Append a signed audit event to the configured database."""
    pg_uri = get_pg_uri()
    db_path = get_db_path()

    if not pg_uri and not db_path:
        return

    init_db()

    payload = event.get("payload", {})
    details = payload.get("details", "")
    if isinstance(details, dict):
        details = json.dumps(details)
    elif not isinstance(details, str):
        details = str(details)

    s3_uri = upload_to_s3(event)

    # Postgres Primary
    if pg_uri and psycopg2:
        try:
            conn = psycopg2.connect(pg_uri)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (timestamp, agent_id, task_id, trace_id, action, details, signature, s3_uri)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                payload.get("timestamp", 0.0),
                str(payload.get("agent_id", "")),
                str(payload.get("task_id", "")),
                str(payload.get("trace_id", "")),
                str(payload.get("action", "")),
                details,
                str(event.get("signature", "")),
                s3_uri
            ))
            conn.commit()
            conn.close()
            return
        except Exception as e:
            logger.error(f"Postgres Error while appending event (falling back): {e}")

    # SQLite Fallback
    if db_path:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (timestamp, agent_id, task_id, trace_id, action, details, signature, s3_uri)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payload.get("timestamp", 0.0),
                str(payload.get("agent_id", "")),
                str(payload.get("task_id", "")),
                str(payload.get("trace_id", "")),
                str(payload.get("action", "")),
                details,
                str(event.get("signature", "")),
                s3_uri
            ))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"SQLite DB Error while appending event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error appending event to SQLite DB: {e}")
