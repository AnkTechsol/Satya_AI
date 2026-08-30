import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.webhook import WebhookExportAdapter
import queue

def test_webhook_export_adapter_trace():
    with patch("src.satya.sdk.adapters.webhook.requests.Session") as mock_session_cls:
        mock_session = mock_session_cls.return_value.__enter__.return_value

        adapter = WebhookExportAdapter(webhook_url="http://test.webhook.local")
        adapter.export_trace("t1", "agent1", "event1", {"foo": "bar"})

        adapter.queue.join()
        adapter.shutdown()

        assert mock_session.post.called
        call_args = mock_session.post.call_args
        assert call_args[0][0] == "http://test.webhook.local"
        assert call_args[1]["json"]["type"] == "trace"
        assert call_args[1]["json"]["trace_id"] == "t1"
        assert call_args[1]["json"]["data"] == {"foo": "bar"}

def test_webhook_export_adapter_log():
    with patch("src.satya.sdk.adapters.webhook.requests.Session") as mock_session_cls:
        mock_session = mock_session_cls.return_value.__enter__.return_value

        adapter = WebhookExportAdapter(webhook_url="http://test.webhook.local")
        adapter.export_log("agent1", "hello", "task1")

        adapter.queue.join()
        adapter.shutdown()

        assert mock_session.post.called
        call_args = mock_session.post.call_args
        assert call_args[0][0] == "http://test.webhook.local"
        assert call_args[1]["json"]["type"] == "log"
        assert call_args[1]["json"]["agent_name"] == "agent1"
        assert call_args[1]["json"]["message"] == "hello"

def test_webhook_export_adapter_queue_full():
    with patch("src.satya.sdk.adapters.webhook.requests.Session") as mock_session_cls:
        mock_session = mock_session_cls.return_value.__enter__.return_value

        # Make post blocking to fill the queue
        def slow_post(*args, **kwargs):
            import time
            time.sleep(0.1)
        mock_session.post.side_effect = slow_post

        adapter = WebhookExportAdapter(webhook_url="http://test.webhook.local", maxsize=1)

        # Fill queue
        adapter.export_log("agent1", "log1")
        adapter.export_log("agent1", "log2")
        adapter.export_log("agent1", "log3")

        adapter.shutdown()
        # Should not crash on queue full
