import pytest
from satya.core.policy_engine import PolicyEngine
from satya.core.agent_registry import AgentRegistry
from satya.schemas.agent import AgentCreate
from satya.schemas.policy import PolicyRead, RuleSchema

@pytest.mark.asyncio
async def test_policy_engine_unregistered_agent():
    # Mock registry so it doesn't try to query the database and hit "no such table"
    class MockRegistry:
        async def get_agent(self, agent_id):
            return None
        async def get_policies_for_agent(self, agent_id):
            return []

    engine = PolicyEngine(MockRegistry())
    result = await engine.evaluate("unknown_agent", {"msg": "hello"})
    assert result.decision == "DENY"
    assert result.violations[0].rule_id == "builtin_agent_not_registered"

@pytest.mark.asyncio
async def test_policy_engine_allow():
    class MockRegistry:
        async def get_agent(self, agent_id):
            return True
        async def get_policies_for_agent(self, agent_id):
            return []

    engine = PolicyEngine(MockRegistry())
    result = await engine.evaluate("known_agent", {"msg": "hello"})
    assert result.decision == "ALLOW"

@pytest.mark.asyncio
async def test_policy_engine_deny():
    class MockRegistry:
        async def get_agent(self, agent_id):
            return True
        async def get_policies_for_agent(self, agent_id):
            return [PolicyRead(
                id="pol_1",
                name="test",
                rules=[RuleSchema(
                    condition="contains_keyword",
                    keywords=["bad"],
                    action="DENY",
                    severity="HIGH",
                    message="Bad word"
                )]
            )]

    engine = PolicyEngine(MockRegistry())
    result = await engine.evaluate("known_agent", {"msg": "this is bad"})
    assert result.decision == "DENY"
    assert len(result.violations) == 1

@pytest.mark.asyncio
async def test_policy_engine_redact():
    class MockRegistry:
        async def get_agent(self, agent_id):
            return True
        async def get_policies_for_agent(self, agent_id):
            return [PolicyRead(
                id="pol_1",
                name="test",
                rules=[RuleSchema(
                    condition="custom_regex",
                    pattern="[0-9]{4}",
                    field="messages[*].content",
                    action="REDACT",
                    severity="MEDIUM",
                    message="Redact numbers"
                )]
            )]

    engine = PolicyEngine(MockRegistry())
    payload = {"messages": [{"content": "My pin is 1234"}]}
    result = await engine.evaluate("known_agent", payload)
    assert result.decision == "REDACT"
    assert result.payload["messages"][0]["content"] == "My pin is [REDACTED]"
