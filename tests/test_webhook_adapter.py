import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("src.satya.sdk.adapters.webhook.socket.getaddrinfo")
@patch("src.satya.sdk.adapters.webhook.requests.Session")
def test_webhook_export_trace(mock_session_cls, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('93.184.216.34', 0))]

    adapter = WebhookExportAdapter(url="https://example.com/webhook", auth_token="secret")
    adapter.export_trace("trace_1", "agent_1", "test_event", {"key": "value"})

    mock_session = mock_session_cls.return_value.__enter__.return_value
    mock_session.post.assert_called_once()
    args, kwargs = mock_session.post.call_args
    assert args[0] == "https://example.com/webhook"
    assert kwargs["json"]["trace_id"] == "trace_1"
    assert kwargs["headers"]["Authorization"] == "Bearer secret"

    mount_calls = mock_session_cls.return_value.__enter__.return_value.mount.call_args_list
    assert len(mount_calls) == 2
    assert mount_calls[0][0][0] == "http://"
    assert mount_calls[1][0][0] == "https://"
    assert mount_calls[0][0][1].target_ip == "93.184.216.34"

@patch("src.satya.sdk.adapters.webhook.socket.getaddrinfo")
@patch("src.satya.sdk.adapters.webhook.requests.Session")
def test_webhook_export_log(mock_session_cls, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('93.184.216.34', 0))]

    adapter = WebhookExportAdapter(url="https://example.com/webhook")
    adapter.export_log("agent_1", "test message", "task_1")

    mock_session = mock_session_cls.return_value.__enter__.return_value
    mock_session.post.assert_called_once()
    args, kwargs = mock_session.post.call_args
    assert args[0] == "https://example.com/webhook"
    assert kwargs["json"]["message"] == "test message"

@patch("src.satya.sdk.adapters.webhook.socket.getaddrinfo")
def test_webhook_unsafe_url(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('127.0.0.1', 0))]

    adapter = WebhookExportAdapter(url="https://localhost/webhook")
    with patch("src.satya.sdk.adapters.webhook.requests.Session") as mock_session_cls:
        adapter.export_log("agent_1", "test message", "task_1")
        mock_session_cls.return_value.__enter__.return_value.post.assert_not_called()
