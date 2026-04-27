import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langfuse import LangfuseAdapter

def test_langfuse_adapter_export_trace():
    adapter = LangfuseAdapter("public", "secret")

    with patch("src.satya.sdk.adapters.langfuse.requests.post") as mock_post:
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert kwargs["auth"] == ("public", "secret")
        assert "timeout" in kwargs

        payload = kwargs["json"]
        assert "batch" in payload
        batch_item = payload["batch"][0]
        assert batch_item["type"] == "trace-create"
        assert batch_item["body"]["name"] == "test_event"
        assert batch_item["body"]["metadata"]["agent_name"] == "test_agent"
        assert batch_item["body"]["metadata"]["key"] == "value"

def test_langfuse_adapter_timeout_handling():
    adapter = LangfuseAdapter("public", "secret")

    with patch("src.satya.sdk.adapters.langfuse.requests.post", side_effect=Exception("Timeout")):
        # Should not raise exception
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
