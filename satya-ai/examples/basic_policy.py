import asyncio
from typing import Dict, Any
import time

# A simple mock script to demonstrate how the Satya API might be used
# in a real application, assuming the Satya server is running locally.

# In reality you would use `httpx` or `requests` to call the endpoints.
# This script prints out the logical flow of interacting with Satya.

def mock_call_satya(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    print(f"Calling POST {endpoint} with payload: {payload}")
    # Mocking the response for demonstration
    if "evaluate" in endpoint:
        if "jailbreak" in str(payload):
            return {"decision": "DENY", "violations": [{"reason": "Restricted keyword detected"}]}
        return {"decision": "ALLOW", "matched_policies": ["pol_001"]}
    return {"id": "mock_id", "status": "success"}

async def run_example():
    print("--- Satya AI Basic Policy Example ---")

    # 1. Register an Agent
    agent_payload = {
        "agent_id": "bot_123",
        "name": "Customer Support Bot",
        "tags": ["support"]
    }
    mock_call_satya("/v1/agents", agent_payload)

    # 2. Create a Policy
    policy_payload = {
        "name": "No Jailbreaks",
        "rules": [{
            "condition": "contains_keyword",
            "keywords": ["jailbreak", "ignore previous instructions"],
            "action": "DENY",
            "severity": "CRITICAL",
            "message": "Attempted prompt injection"
        }]
    }
    policy_response = mock_call_satya("/v1/policies", policy_payload)

    # 3. Attach Policy to Agent
    mock_call_satya(f"/v1/policies/{policy_response['id']}/attach/bot_123", {})

    # 4. Evaluate an Allowed Payload
    allow_payload = {
        "agent_id": "bot_123",
        "payload": {"messages": [{"role": "user", "content": "Hello, how can I reset my password?"}]}
    }
    print("Evaluating SAFE request...")
    res1 = mock_call_satya("/v1/evaluate", allow_payload)
    print(f"Result: {res1['decision']}\n")

    # 5. Evaluate a Denied Payload
    deny_payload = {
        "agent_id": "bot_123",
        "payload": {"messages": [{"role": "user", "content": "jailbreak system instructions"}]}
    }
    print("Evaluating UNSAFE request...")
    res2 = mock_call_satya("/v1/evaluate", deny_payload)
    print(f"Result: {res2['decision']}, Violations: {res2.get('violations')}\n")

if __name__ == "__main__":
    asyncio.run(run_example())
