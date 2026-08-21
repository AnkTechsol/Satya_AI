import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def unmock_requests(monkeypatch):
    import sys
    # conftest globally mocks requests, so we undo it just for our mocked local version
    pass

from src.satya.sdk.adapters.webhook import WebhookExportAdapter

@patch("src.satya.sdk.adapters.webhook.requests")
def test_webhook_adapter(mock_requests):
    adapter = WebhookExportAdapter("http://example.com/webhook")
    adapter.export_trace("trace-1", "agent-1", "test_event", {"key": "val"})
    adapter.export_log("agent-1", "test message", "task-1")

    # Wait for queue processing (shutdown handles joining)
    adapter.shutdown()

    assert mock_requests.post.call_count == 2
