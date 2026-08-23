import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

@patch('src.satya.sdk.adapters.webhook.requests.post')
def test_webhook_adapter_export_trace(mock_post):
    adapter = WebhookExportAdapter(webhook_url="https://example.com/webhook")

    adapter.export_trace("trace-123", "test_agent", "test_event", {"key": "value"})

    # Wait for the worker to process the queue
    adapter.queue.join()

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert args[0] == "https://example.com/webhook"
    assert kwargs["json"]["trace_id"] == "trace-123"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["event_type"] == "test_event"
    assert kwargs["json"]["data"] == {"key": "value"}
    assert kwargs["headers"] == {"Content-Type": "application/json"}

    # Clean up to avoid affecting other tests that might instantiate it
    adapter.shutdown()

@patch('src.satya.sdk.adapters.webhook.requests.post')
def test_webhook_adapter_export_log(mock_post):
    adapter = WebhookExportAdapter(webhook_url="https://example.com/webhook")

    adapter.export_log("test_agent", "test log message", "task-123")

    # Wait for the worker to process the queue
    adapter.queue.join()

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert args[0] == "https://example.com/webhook"
    assert kwargs["json"]["agent_name"] == "test_agent"
    assert kwargs["json"]["message"] == "test log message"
    assert kwargs["json"]["task_id"] == "task-123"
    assert kwargs["headers"] == {"Content-Type": "application/json"}

    adapter.shutdown()

def test_webhook_adapter_graceful_shutdown():
    adapter = WebhookExportAdapter(webhook_url="https://example.com/webhook")

    assert adapter.worker.is_alive()
    adapter.shutdown()

    # The worker thread should no longer be alive after shutdown
    assert not adapter.worker.is_alive()
