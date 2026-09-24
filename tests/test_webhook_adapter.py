import sys
import queue
from unittest.mock import patch
import pytest

sys.path.insert(0, "src")
from satya.sdk.adapters.webhook import WebhookAdapter

@patch("satya.sdk.adapters.webhook.requests.post")
def test_export_trace(mock_post):
    adapter = WebhookAdapter("http://localhost:8080")
    adapter.export_trace("test_trace", "test_agent", "test_event", {"key": "val"})
    adapter.queue.join()
    mock_post.assert_called_once()
    adapter.shutdown()

@patch("satya.sdk.adapters.webhook.requests.post")
def test_export_log(mock_post):
    adapter = WebhookAdapter("http://localhost:8080")
    adapter.export_log("test_agent", "test_msg", "test_task")
    adapter.queue.join()
    mock_post.assert_called_once()
    adapter.shutdown()

@patch("satya.sdk.adapters.webhook.requests.post")
def test_ssrf_mitigation_bad_url(mock_post):
    adapter = WebhookAdapter("ftp://localhost")
    adapter.export_log("test_agent", "test_msg")
    adapter.queue.join()
    mock_post.assert_not_called()
    adapter.shutdown()

def test_shutdown_idempotent():
    adapter = WebhookAdapter("http://localhost:8080")
    adapter.shutdown()
    adapter.shutdown() # Should not raise
