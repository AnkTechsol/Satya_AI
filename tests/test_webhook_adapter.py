import pytest
import time
from unittest.mock import patch
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("src.satya.sdk.adapters.webhook.requests.post")
def test_webhook_export_trace(mock_post):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_trace("trace-1", "test_agent", "test_event", {"key": "value"})

    # Wait for the worker thread to process the queue
    time.sleep(0.5)

    adapter.shutdown()

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"]["type"] == "trace"
    assert kwargs["json"]["trace_id"] == "trace-1"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["event_type"] == "test_event"
    assert kwargs["json"]["data"] == {"key": "value"}

@patch("src.satya.sdk.adapters.webhook.requests.post")
def test_webhook_export_log(mock_post):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_log("test_agent", "Test message", "task-1")

    # Wait for the worker thread to process the queue
    time.sleep(0.5)

    adapter.shutdown()

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"]["type"] == "log"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["task_id"] == "task-1"
    assert kwargs["json"]["message"] == "Test message"
