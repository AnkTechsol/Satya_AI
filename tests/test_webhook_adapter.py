import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, "src")
from satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("satya.sdk.adapters.webhook.requests.post")
def test_export_trace(mock_post):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_trace("trace-1", "agent-1", "test_event", {"key": "value"})
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["trace_id"] == "trace-1"
    assert kwargs["json"]["agent_name"] == "agent-1"
    assert kwargs["json"]["key"] == "value"

@patch("satya.sdk.adapters.webhook.requests.post")
def test_export_log(mock_post):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_log("agent-1", "test log message", "task-1")
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["agent_name"] == "agent-1"
    assert kwargs["json"]["message"] == "test log message"
    assert kwargs["json"]["task_id"] == "task-1"
