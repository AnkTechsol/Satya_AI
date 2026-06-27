import pytest
from unittest.mock import patch, MagicMock
from satya.sdk.adapters.langsmith import LangSmithAdapter

@patch("satya.sdk.adapters.langsmith.requests.post")
def test_langsmith_adapter_export_trace(mock_post):
    adapter = LangSmithAdapter(api_key="test_key")
    adapter.export_trace("trace123", "test_agent", "trace_prompt", {"prompt": "hello", "response": "world"})

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert "runs" in args[0]

    payload = kwargs["json"]
    assert payload["name"] == "trace_prompt"
    assert payload["extra"]["metadata"]["agent_name"] == "test_agent"
    assert payload["inputs"]["prompt"] == "hello"
    assert payload["outputs"]["response"] == "world"

@patch("satya.sdk.adapters.langsmith.requests.post")
def test_langsmith_adapter_timeout_handling(mock_post):
    mock_post.side_effect = Exception("Timeout")
    adapter = LangSmithAdapter(api_key="test_key")
    # Should not raise exception
    adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
