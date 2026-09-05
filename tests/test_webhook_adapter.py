import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, "src")
from satya.sdk.adapters.webhook import WebhookAdapter

@patch("satya.sdk.adapters.webhook.socket.getaddrinfo")
@patch("satya.sdk.adapters.webhook.requests.post")
def test_export_trace(mock_post, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(None, None, None, None, ("8.8.8.8",))]
    adapter = WebhookAdapter("https://example.com/webhook")
    adapter.export_trace("test_trace", "test_agent", "test_event", {"key": "val"})
    adapter.queue.join()
    mock_post.assert_called_once()
    adapter.shutdown()

@patch("satya.sdk.adapters.webhook.socket.getaddrinfo")
@patch("satya.sdk.adapters.webhook.requests.post")
def test_export_log(mock_post, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(None, None, None, None, ("8.8.8.8",))]
    adapter = WebhookAdapter("https://example.com/webhook")
    adapter.export_log("test_agent", "msg", "t1")
    adapter.queue.join()
    mock_post.assert_called_once()
    adapter.shutdown()