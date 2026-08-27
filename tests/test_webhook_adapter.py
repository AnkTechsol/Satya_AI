import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("src.satya.sdk.adapters.webhook.requests.post")
def test_webhook_export_trace(mock_post):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
    adapter.shutdown()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"] == {
        "type": "trace",
        "trace_id": "trace123",
        "agent_name": "test_agent",
        "event_type": "test_event",
        "data": {"key": "value"}
    }

@patch("src.satya.sdk.adapters.webhook.requests.post")
def test_webhook_export_log(mock_post):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_log("test_agent", "Test message", "task456")
    adapter.shutdown()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"] == {
        "type": "log",
        "agent_name": "test_agent",
        "message": "Test message",
        "task_id": "task456"
    }
