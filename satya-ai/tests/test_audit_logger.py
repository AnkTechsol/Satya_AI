import pytest
import asyncio
from satya.core.audit_logger import AuditLogger
from satya.schemas.audit import AuditEventSchema, AuditQueryFilters

@pytest.mark.asyncio
async def test_audit_logger(db_session, monkeypatch):
    # Mock AsyncSessionLocal to use our test session
    class MockSessionLocal:
        async def __aenter__(self):
            return db_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr("satya.core.audit_logger.AsyncSessionLocal", MockSessionLocal)

    logger = AuditLogger()
    await logger.start()

    event = AuditEventSchema(
        event_id="test_evt_1",
        timestamp="2024-01-01T00:00:00Z",
        agent_id="agent_1",
        decision="ALLOW",
        payload_hash="hash",
        latency_ms=10.0
    )

    await logger.log(event)
    await logger.stop() # Stop flushes queue

    # Query it back
    filters = AuditQueryFilters(agent_id="agent_1")
    results = await logger.query(filters)
    assert len(results) >= 1
    assert results[0].agent_id == "agent_1"

    summary = await logger.get_summary()
    assert summary.total_events >= 1

@pytest.mark.asyncio
async def test_audit_export(client, monkeypatch):
    from satya.core.audit_logger import AuditLogger

    # To test export and endpoints fully
    await client.post("/v1/agents", json={"agent_id": "audit_agent", "name": "Audit"})

    # Evaluate
    await client.post("/v1/evaluate", json={
        "agent_id": "audit_agent",
        "payload": {"text": "hello"}
    })

    await asyncio.sleep(0.1) # allow worker to process

    # Export NDJSON
    res = await client.get("/v1/audit/export?agent_id=audit_agent")
    assert res.status_code == 200
    assert "agent_id" in res.text

    # Summary
    res = await client.get("/v1/audit/summary")
    assert res.status_code == 200
    assert "total_events" in res.json()
