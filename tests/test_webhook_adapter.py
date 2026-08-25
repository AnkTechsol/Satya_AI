import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

def test_webhook_adapter_export_trace():
    adapter = WebhookExportAdapter("http://example.com/webhook")
    with patch("src.satya.sdk.adapters.webhook.requests.post") as mock_post:
        adapter.export_trace("trace1", "agent1", "event1", {"key": "val"})
        adapter.queue.join()
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["type"] == "trace"
        assert kwargs["json"]["trace_id"] == "trace1"
        assert kwargs["json"]["agent_name"] == "agent1"
        assert kwargs["json"]["event_type"] == "event1"
        assert kwargs["json"]["data"]["key"] == "val"
    adapter.shutdown()

def test_webhook_adapter_export_log():
    adapter = WebhookExportAdapter("http://example.com/webhook")
    with patch("src.satya.sdk.adapters.webhook.requests.post") as mock_post:
        adapter.export_log("agent1", "msg1", "task1")
        adapter.queue.join()
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["type"] == "log"
        assert kwargs["json"]["agent_name"] == "agent1"
        assert kwargs["json"]["message"] == "msg1"
        assert kwargs["json"]["task_id"] == "task1"
    adapter.shutdown()

def test_webhook_adapter_shutdown_idempotent():
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.shutdown()
    adapter.shutdown() # Should not deadlock
