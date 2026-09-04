import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, "src")
from satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("satya.sdk.adapters.webhook.requests.post")
def test_webhook_export_trace_and_log(mock_post):
    adapter = WebhookExportAdapter("http://test.com/webhook")
    adapter.export_trace("trace123", "agent1", "start", {"foo": "bar"})
    adapter.export_log("agent1", "Doing work", "task1")

    adapter.queue.join()

    assert mock_post.call_count == 2

    trace_call = mock_post.call_args_list[0]
    assert trace_call.kwargs["json"]["type"] == "trace"
    assert trace_call.kwargs["json"]["trace_id"] == "trace123"

    log_call = mock_post.call_args_list[1]
    assert log_call.kwargs["json"]["type"] == "log"
    assert log_call.kwargs["json"]["message"] == "Doing work"

    adapter.shutdown()