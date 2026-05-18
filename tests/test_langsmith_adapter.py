import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

def test_langsmith_adapter_export_trace():
    adapter = LangSmithAdapter("test_api_key", project_name="test_project")

    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert kwargs["headers"]["x-api-key"] == "test_api_key"
        assert "timeout" in kwargs

        payload = kwargs["json"]
        assert payload["name"] == "test_event"
        assert payload["run_type"] == "chain"
        assert payload["trace_id"] == "trace123"
        assert payload["session_name"] == "test_project"

        assert payload["extra"]["metadata"]["agent_name"] == "test_agent"
        assert payload["extra"]["metadata"]["key"] == "value"

def test_langsmith_adapter_timeout_handling():
    adapter = LangSmithAdapter("test_api_key")

    with patch("src.satya.sdk.adapters.langsmith.requests.post", side_effect=Exception("Timeout")):
        # Should not raise exception
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})