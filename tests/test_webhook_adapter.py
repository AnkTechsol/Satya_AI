import sys
import pytest
from unittest.mock import patch, MagicMock

# Local monkeypatching for requests to bypass global mock in conftest
import src.satya.sdk.adapters.webhook

@patch('src.satya.sdk.adapters.webhook.requests')
def test_webhook_adapter(mock_requests):
    from src.satya.sdk.adapters.webhook import WebhookExportAdapter

    target_url = "https://example.com/webhook"
    adapter = WebhookExportAdapter(target_url)

    # Test exporting trace
    adapter.export_trace(
        trace_id="trace123",
        agent_name="test_agent",
        event_type="task_created",
        data={"key": "value"}
    )

    # Test exporting log
    adapter.export_log(
        agent_name="test_agent",
        message="This is a test log",
        task_id="task123"
    )

    # Wait for the queue to process
    adapter.queue.join()

    # Verify post calls
    assert mock_requests.post.call_count == 2

    calls = mock_requests.post.call_args_list
    trace_call = calls[0]
    log_call = calls[1]

    assert trace_call[0][0] == target_url
    assert trace_call[1]['json']['type'] == "trace"
    assert trace_call[1]['json']['trace_id'] == "trace123"

    assert log_call[0][0] == target_url
    assert log_call[1]['json']['type'] == "log"
    assert log_call[1]['json']['message'] == "This is a test log"

    # Verify graceful shutdown
    adapter.shutdown()
    assert not adapter.worker_thread.is_alive()

@patch('src.satya.sdk.adapters.webhook.requests.post')
def test_webhook_adapter_exception_handling(mock_post):
    mock_post.side_effect = Exception("Simulated network failure")

    from src.satya.sdk.adapters.webhook import WebhookExportAdapter
    adapter = WebhookExportAdapter("https://example.com/webhook")

    # This should not crash the main thread
    adapter.export_trace(
        trace_id="trace123",
        agent_name="test_agent",
        event_type="task_created",
        data={}
    )

    # Wait for queue to process, verify it swallows exception and moves on
    adapter.queue.join()

    assert mock_post.called
    adapter.shutdown()
