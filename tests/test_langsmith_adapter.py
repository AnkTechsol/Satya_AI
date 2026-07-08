import uuid
from unittest.mock import patch
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

def test_langsmith_adapter():
    adapter = LangSmithAdapter(api_key="test_key")
    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("unknown", "agent1", "prompt", {"prompt": "hello", "response": "world"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        payload = kwargs["json"]
        assert "id" in payload
        assert uuid.UUID(payload["id"])
        assert payload["name"] == "prompt"
        assert payload["run_type"] == "llm"
        assert payload["inputs"] == "hello"
        assert payload["outputs"] == "world"
        assert "end_time" in payload