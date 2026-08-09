import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, "src")
from satya.sdk.adapters.webhook import WebhookAdapter

@patch("satya.sdk.adapters.webhook.requests.post")
def test_webhook_adapter_export_trace(mock_post):
    adapter = WebhookAdapter("http://example.com/webhook")
    adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["type"] == "trace"
    assert kwargs["json"]["trace_id"] == "trace123"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["event_type"] == "test_event"
    assert kwargs["json"]["data"] == {"key": "value"}
    assert kwargs["timeout"] == 2

@patch("satya.sdk.adapters.webhook.requests.post")
def test_webhook_adapter_export_log(mock_post):
    adapter = WebhookAdapter("http://example.com/webhook")
    adapter.export_log("test_agent", "test_message", "task123")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["type"] == "log"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["message"] == "test_message"
    assert kwargs["json"]["task_id"] == "task123"
    assert kwargs["timeout"] == 2

@patch("satya.sdk.adapters.webhook.requests.post", side_effect=Exception("Timeout"))
def test_webhook_adapter_timeout_handling(mock_post):
    adapter = WebhookAdapter("http://example.com/webhook")
    # Should not raise exception
    adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
    adapter.export_log("test_agent", "test_message", "task123")
