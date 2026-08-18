import pytest
import time
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookAdapter

@patch('src.satya.sdk.adapters.webhook.requests.post')
def test_webhook_adapter_export_trace(mock_post):
    adapter = WebhookAdapter("http://test.local")
    adapter.export_trace("t1", "agent1", "event1", {"key": "value"})
    adapter.queue.join()
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["trace_id"] == "t1"
    assert kwargs["json"]["agent_name"] == "agent1"
    assert kwargs["json"]["type"] == "trace"
    adapter.shutdown()

@patch('src.satya.sdk.adapters.webhook.requests.post')
def test_webhook_adapter_export_log(mock_post):
    adapter = WebhookAdapter("http://test.local")
    adapter.export_log("agent1", "msg", "task1")
    adapter.queue.join()
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["message"] == "msg"
    assert kwargs["json"]["agent_name"] == "agent1"
    assert kwargs["json"]["type"] == "log"
    adapter.shutdown()
