import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_evaluate_endpoint_integration(client: AsyncClient):
    # 1. Create Agent
    await client.post("/v1/agents", json={
        "agent_id": "test_agent_2",
        "name": "Integration Agent"
    })

    # 2. Create Policy
    pol_res = await client.post("/v1/policies", json={
        "name": "Block Secrets",
        "rules": [{
            "condition": "contains_keyword",
            "keywords": ["secret_key"],
            "action": "DENY",
            "severity": "CRITICAL",
            "message": "No secrets allowed"
        }]
    })
    policy_id = pol_res.json()["id"]

    # 3. Attach
    await client.post(f"/v1/policies/{policy_id}/attach/test_agent_2")

    # 4. Evaluate ALLOW
    res_allow = await client.post("/v1/evaluate", json={
        "agent_id": "test_agent_2",
        "payload": {"text": "hello world"}
    })
    assert res_allow.status_code == 200
    assert res_allow.json()["decision"] == "ALLOW"

    # 5. Evaluate DENY
    res_deny = await client.post("/v1/evaluate", json={
        "agent_id": "test_agent_2",
        "payload": {"text": "here is my secret_key"}
    })
    # Should be 403 as per requirements
    assert res_deny.status_code == 403
    assert res_deny.json()["decision"] == "DENY"

    # Let the background task write to audit queue
    import asyncio
    await asyncio.sleep(0.2)

    # 6. Check Audit Log
    res_audit = await client.get("/v1/audit/events?agent_id=test_agent_2")
    assert res_audit.status_code == 200
    events = res_audit.json()
    assert len(events) >= 2
