import pytest
import time
from unittest.mock import patch
from src.satya.sdk.adapters.webhook import WebhookExportAdapter

def test_webhook_adapter_export_trace():
    adapter = WebhookExportAdapter(["http://example.com/webhook"])

    with patch("src.satya.sdk.adapters.webhook.requests.post") as mock_post:
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})
        # wait a bit for queue processing
        time.sleep(0.1)
        adapter.shutdown()

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["trace_id"] == "trace123"
        assert kwargs["json"]["agent_name"] == "test_agent"
        assert kwargs["json"]["event"] == "test_event"
        assert kwargs["json"]["data"] == {"key": "value"}
        assert "timeout" in kwargs
