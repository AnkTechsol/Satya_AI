import pytest
from unittest.mock import patch
import sys

sys.path.insert(0, "src")
from satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("satya.sdk.adapters.webhook.requests.post")
def test_webhook_adapter_export_trace(mock_post):
    adapter = WebhookExportAdapter("http://test-webhook.com")
    adapter.export_trace("trace-123", "test_agent", "test_event", {"key": "value"})
    adapter.queue.join()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://test-webhook.com"
    assert kwargs["json"]["type"] == "trace"
    assert kwargs["json"]["trace_id"] == "trace-123"
    assert kwargs["json"]["agent_name"] == "test_agent"

    adapter.shutdown()

@patch("satya.sdk.adapters.webhook.requests.post")
def test_webhook_adapter_export_log(mock_post):
    adapter = WebhookExportAdapter("http://test-webhook.com")
    adapter.export_log("test_agent", "test message", "task-123")
    adapter.queue.join()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://test-webhook.com"
    assert kwargs["json"]["type"] == "log"
    assert kwargs["json"]["message"] == "test message"
    assert kwargs["json"]["agent_name"] == "test_agent"

    adapter.shutdown()