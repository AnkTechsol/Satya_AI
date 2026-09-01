import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookAdapter

@patch("src.satya.sdk.adapters.webhook.requests.Session")
def test_webhook_adapter_trace(mock_session_cls):
    mock_session = mock_session_cls.return_value.__enter__.return_value
    adapter = WebhookAdapter(webhook_url="http://example.com/webhook")

    adapter.export_trace(trace_id="123", agent_name="AgentX", event_type="start", data={"key": "val"})
    adapter.shutdown()

    assert mock_session.post.call_count == 1
    args, kwargs = mock_session.post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"]["type"] == "trace"
    assert kwargs["json"]["trace_id"] == "123"

@patch("src.satya.sdk.adapters.webhook.requests.Session")
def test_webhook_adapter_log(mock_session_cls):
    mock_session = mock_session_cls.return_value.__enter__.return_value
    adapter = WebhookAdapter(webhook_url="http://example.com/webhook")

    adapter.export_log(agent_name="AgentY", message="Log msg", task_id="t1")
    adapter.shutdown()

    assert mock_session.post.call_count == 1
    args, kwargs = mock_session.post.call_args
    assert args[0] == "http://example.com/webhook"
    assert kwargs["json"]["type"] == "log"
    assert kwargs["json"]["message"] == "Log msg"
