import pytest
from httpx import AsyncClient
from satya.schemas.agent import AgentCreate

pytestmark = pytest.mark.asyncio

async def test_register_and_get_agent(client: AsyncClient):
    # Register
    payload = {
        "agent_id": "test_agent_1",
        "name": "Test Agent",
        "tags": ["test"]
    }
    response = await client.post("/v1/agents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "test_agent_1"

    # Get
    response = await client.get("/v1/agents/test_agent_1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Agent"

    # Update
    update_payload = {"team": "testing_team"}
    response = await client.patch("/v1/agents/test_agent_1", json=update_payload)
    assert response.status_code == 200
    assert response.json()["team"] == "testing_team"

    # List
    response = await client.get("/v1/agents")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Delete
    response = await client.delete("/v1/agents/test_agent_1")
    assert response.status_code == 200

    # Verify deleted
    response = await client.get("/v1/agents/test_agent_1")
    assert response.status_code == 404
