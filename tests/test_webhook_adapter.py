import pytest
import sys
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookAdapter

@patch('src.satya.sdk.adapters.webhook.requests')
def test_webhook_adapter_export_trace(mock_requests):
    mock_post = mock_requests.post
    adapter = WebhookAdapter(webhook_url="http://example.com/webhook")

    adapter.export_trace(
        trace_id="trace123",
        agent_name="test_agent",
        event_type="test_event",
        data={"key": "value"}
    )

    # Wait for the worker thread to process the item in the queue
    adapter.queue.join()

    # Ensure requests.post was called
    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs['json']['type'] == "trace"
    assert kwargs['json']['trace_id'] == "trace123"
    assert kwargs['json']['agent_name'] == "test_agent"
    assert kwargs['json']['event_type'] == "test_event"
    assert kwargs['json']['data'] == {"key": "value"}

    adapter.shutdown()

@patch('src.satya.sdk.adapters.webhook.requests')
def test_webhook_adapter_export_log(mock_requests):
    mock_post = mock_requests.post
    adapter = WebhookAdapter(webhook_url="http://example.com/webhook")

    adapter.export_log(
        agent_name="test_agent",
        message="test log message",
        task_id="task123"
    )

    # Wait for the worker thread to process the item in the queue
    adapter.queue.join()

    # Ensure requests.post was called
    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs['json']['type'] == "log"
    assert kwargs['json']['agent_name'] == "test_agent"
    assert kwargs['json']['message'] == "test log message"
    assert kwargs['json']['task_id'] == "task123"

    adapter.shutdown()

@patch('src.satya.sdk.adapters.webhook.requests')
def test_webhook_adapter_swallows_exception(mock_requests):
    mock_post = mock_requests.post
    # Simulate a network error
    mock_post.side_effect = Exception("Network timeout")

    adapter = WebhookAdapter(webhook_url="http://example.com/webhook")

    adapter.export_log(
        agent_name="test_agent",
        message="test log message"
    )

    # Wait for the worker thread to process the item in the queue.
    # If the exception is not swallowed, the queue might not join or the test will fail
    adapter.queue.join()

    # Ensure requests.post was called
    assert mock_post.called

    adapter.shutdown()
