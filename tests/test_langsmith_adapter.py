import uuid
from src.satya.sdk.adapters.langsmith import LangSmithAdapter
import requests_mock

def test_langsmith_adapter():
    adapter = LangSmithAdapter(api_key="test_key")
    with requests_mock.Mocker() as m:
        m.post("https://api.smith.langchain.com/runs", text='{"id": "test"}')
        adapter.export_trace("unknown", "agent1", "prompt", {"prompt": "hello", "response": "world"})

        assert m.called
        request = m.last_request
        payload = request.json()
        assert "id" in payload
        assert uuid.UUID(payload["id"])
        assert payload["name"] == "prompt"
        assert payload["run_type"] == "llm"
        assert payload["inputs"] == "hello"
        assert payload["outputs"] == "world"
        assert "end_time" in payload
