import pytest
from unittest.mock import patch, MagicMock
from satya.sdk.adapters.webhook import WebhookAdapter
import queue
import socket
import ipaddress

def test_webhook_adapter_ssrf_blocked():
    adapter = WebhookAdapter("https://example.com/api/webhook")

    with patch('socket.gethostbyname', return_value="127.0.0.1"), \
         patch('satya.sdk.adapters.webhook.requests.post') as mock_post:
        adapter.export_log("test_agent", "test message")
        adapter.queue.join()
        adapter.shutdown()
        mock_post.assert_not_called()

def test_webhook_adapter_success():
    adapter = WebhookAdapter("https://example.com/api/webhook")

    with patch('socket.gethostbyname', return_value="8.8.8.8"), \
         patch('satya.sdk.adapters.webhook.requests.post') as mock_post:
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
        adapter.queue.join()
        adapter.shutdown()

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://8.8.8.8:443/api/webhook"
        assert kwargs['json']['type'] == "trace"
        assert kwargs['json']['trace_id'] == "trace123"

def test_webhook_adapter_invalid_scheme():
    with pytest.raises(ValueError):
        WebhookAdapter("ftp://example.com")
