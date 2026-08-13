import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.webhook import WebhookAdapter

@patch('src.satya.sdk.adapters.webhook.requests.Session')
def test_webhook_adapter_export_trace(mock_session_cls):
    adapter = WebhookAdapter("https://example.com/webhook")
    adapter.export_trace("trace-123", "test_agent", "status_updated", {"status": "done"})

    mock_session_cls.return_value.post.assert_called_once()
    args, kwargs = mock_session_cls.return_value.post.call_args
    assert args[0] == "https://example.com/webhook"
    assert kwargs["json"]["trace_id"] == "trace-123"
    assert kwargs["json"]["event_type"] == "status_updated"
    assert kwargs["json"]["data"] == {"status": "done"}

@patch('src.satya.sdk.adapters.webhook.requests.Session')
def test_webhook_adapter_export_log(mock_session_cls):
    adapter = WebhookAdapter("http://localhost:8080/logs")
    adapter.export_log("test_agent", "Test message", "task-456")

    mock_session_cls.return_value.post.assert_called_once()
    args, kwargs = mock_session_cls.return_value.post.call_args
    assert args[0] == "http://localhost:8080/logs"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["message"] == "Test message"
    assert kwargs["json"]["task_id"] == "task-456"

@patch('src.satya.sdk.adapters.webhook.requests.Session')
def test_webhook_adapter_swallows_exception(mock_session_cls):
    mock_session_cls.return_value.post.side_effect = Exception("Timeout")
    adapter = WebhookAdapter("http://error.com")
    # Should not raise an exception
    adapter.export_trace("trace-1", "test_agent", "test", {})
