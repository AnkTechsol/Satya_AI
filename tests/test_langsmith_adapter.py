import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_langsmith_adapter_export(mock_post):
    adapter = LangSmithAdapter(api_key="test-key", project_name="test-project")
    adapter.export_trace("trace-1", "agent-x", "test_event", {"key": "value"})

    mock_post.assert_called_once()
    call_args, call_kwargs = mock_post.call_args

    assert call_args[0] == "https://api.smith.langchain.com/runs"
    assert call_kwargs["headers"]["x-api-key"] == "test-key"
    assert call_kwargs["json"]["id"] == "trace-1"
    assert call_kwargs["json"]["name"] == "test_event"
    assert call_kwargs["json"]["session_name"] == "test-project"
    assert call_kwargs["json"]["extra"]["metadata"]["agent_name"] == "agent-x"
    assert call_kwargs["json"]["extra"]["metadata"]["key"] == "value"
    assert call_kwargs["timeout"] == 2
