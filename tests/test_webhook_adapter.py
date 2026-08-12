import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookAdapter

def test_webhook_adapter_export_trace():
    adapter = WebhookAdapter("http://test.webhook")

    with patch("src.satya.sdk.adapters.webhook.requests.post") as mock_post:
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert args[0] == "http://test.webhook"
        assert "timeout" in kwargs

        payload = kwargs["json"]
        assert payload["type"] == "trace"
        assert payload["trace_id"] == "trace123"
        assert payload["agent_name"] == "test_agent"
        assert payload["event_type"] == "test_event"
        assert payload["data"]["key"] == "value"

def test_webhook_adapter_export_log():
    adapter = WebhookAdapter("http://test.webhook")

    with patch("src.satya.sdk.adapters.webhook.requests.post") as mock_post:
        adapter.export_log("test_agent", "test message", "task123")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert args[0] == "http://test.webhook"
        assert "timeout" in kwargs

        payload = kwargs["json"]
        assert payload["type"] == "log"
        assert payload["agent_name"] == "test_agent"
        assert payload["task_id"] == "task123"
        assert payload["message"] == "test message"

def test_webhook_adapter_timeout_handling():
    adapter = WebhookAdapter("http://test.webhook")

    with patch("src.satya.sdk.adapters.webhook.requests.post", side_effect=Exception("Timeout")):
        # Should not raise exception
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
        adapter.export_log("test_agent", "test message", "task123")