from unittest.mock import patch
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

def test_langsmith_adapter_export_trace():
    adapter = LangSmithAdapter(api_key="test-key")

    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace(
            trace_id="test-trace-123",
            agent_name="test_agent",
            event_type="test_event",
            data={"key": "value"}
        )

        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert kwargs["timeout"] == 2
        assert "json" in kwargs
        assert kwargs["json"]["name"] == "test_event"
        assert kwargs["json"]["extra"]["agent_name"] == "test_agent"
        assert kwargs["headers"]["x-api-key"] == "test-key"

def test_langsmith_adapter_timeout_handling():
    adapter = LangSmithAdapter(api_key="test-key")

    with patch("src.satya.sdk.adapters.langsmith.requests.post", side_effect=Exception("Timeout")):
        # This should not raise an exception
        adapter.export_trace(
            trace_id="test-trace-123",
            agent_name="test_agent",
            event_type="test_event",
            data={"key": "value"}
        )
