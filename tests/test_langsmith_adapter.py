import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

def test_langsmith_export_trace():
    adapter = LangSmithAdapter(api_key="test_key")
    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("trace_123", "test_agent", "test_event", {"key": "value"})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "runs" in args[0]
        assert kwargs["headers"]["x-api-key"] == "test_key"
        assert kwargs["json"]["name"] == "test_event"
