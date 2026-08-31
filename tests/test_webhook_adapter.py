import pytest
import sys
from unittest.mock import patch
from src.satya.sdk.adapters.webhook import WebhookAdapter

def test_webhook_adapter():
    with patch('src.satya.sdk.adapters.webhook.dispatch') as mock_dispatch:
        adapter = WebhookAdapter()
        adapter.export_trace("t1", "agent1", "start", {"k": "v"})
        adapter.export_log("agent1", "msg", "task1")

        adapter.shutdown()

        assert mock_dispatch.call_count == 2
