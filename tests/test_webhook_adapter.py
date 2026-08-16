import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("src.satya.sdk.adapters.webhook.requests.post")
def test_webhook_adapter_trace(mock_post, monkeypatch):
    import time

    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_trace("trace123", "agent1", "event1", {"key": "value"})

    # Wait for the background thread to process the queue
    adapter._queue.join()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"]["trace_id"] == "trace123"
    assert kwargs["json"]["data"] == {"key": "value"}
    assert kwargs["json"]["timestamp"].endswith("Z")
    assert "+00:00" not in kwargs["json"]["timestamp"]
    adapter.shutdown()

@patch("src.satya.sdk.adapters.webhook.requests.post")
def test_webhook_adapter_log(mock_post, monkeypatch):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_log("agent1", "msg", "task1")

    adapter._queue.join()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"]["message"] == "msg"
    assert kwargs["json"]["task_id"] == "task1"
    assert kwargs["json"]["timestamp"].endswith("Z")
    assert "+00:00" not in kwargs["json"]["timestamp"]
    adapter.shutdown()
