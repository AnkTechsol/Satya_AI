import httpx
from typing import Dict, Any, Optional

class SatyaPolicyViolation(Exception):
    def __init__(self, violations: list):
        self.violations = violations
        super().__init__(f"Satya Governance Blocked Request: {violations}")

class SatyaProxy:
    """
    Drop-in proxy for OpenAI that routes requests through Satya AI Governance.
    """
    def __init__(self, agent_id: str, satya_url: str = "http://localhost:8000", api_key: str = "DEMO_KEY"):
        self.agent_id = agent_id
        self.satya_url = satya_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(headers={"X-Satya-Key": self.api_key})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def chat(self, messages: list, model: str, **kwargs) -> Dict[str, Any]:
        payload = {"messages": messages, "model": model, **kwargs}

        # 1. Evaluate via Satya
        eval_req = {
            "agent_id": self.agent_id,
            "payload": payload,
            "context": {"source": "openai_proxy"}
        }

        # Expect 403 on DENY, need to handle it gracefully in httpx
        try:
            response = await self.client.post(f"{self.satya_url}/v1/evaluate", json=eval_req)

            if response.status_code == 403:
                result = response.json()
                raise SatyaPolicyViolation(result.get("violations", []))

            response.raise_for_status()
            result = response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise SatyaPolicyViolation(e.response.json().get("violations", []))
            raise e

        # 2. Check Decision
        decision = result.get("decision", "ALLOW")

        if decision == "DENY":
            raise SatyaPolicyViolation(result.get("violations", []))

        # 3. Use potentially redacted payload
        final_payload = result.get("payload") or payload

        # 4. Forward to real OpenAI (Mocked here)
        print(f"[OpenAI Mock] Sending payload: {final_payload}")
        return {"choices": [{"message": {"role": "assistant", "content": "Mock OpenAI Response"}}]}

# Example usage
async def main():
    async with SatyaProxy("my_agent") as proxy:
        try:
            response = await proxy.chat(
                messages=[{"role": "user", "content": "Write a python script"}],
                model="gpt-4o"
            )
            print("Response:", response)
        except SatyaPolicyViolation as e:
            print("Blocked by Policy:", e)

if __name__ == "__main__":
    import asyncio
    # asyncio.run(main()) # Uncomment when server is running
