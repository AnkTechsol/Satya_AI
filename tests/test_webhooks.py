import pytest
import os
import json
import sys
sys.path.insert(0, os.path.abspath("src"))

from unittest.mock import patch
from satya.core import webhooks
from satya.core.storage import SATYA_DIR


@pytest.fixture(autouse=True)
def cleanup_webhooks():
    path = webhooks.get_webhooks_path()
    if os.path.exists(path):
        os.remove(path)
    yield
    if os.path.exists(path):
        os.remove(path)

@patch("satya.core.webhooks.socket.getaddrinfo")
def test_add_and_remove_webhook(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('93.184.216.34', 0))]
    url = "https://example.com/webhook"

    assert webhooks.add_webhook(url) is True

    loaded = webhooks.load_webhooks()
    assert len(loaded) == 1
    assert loaded[0]["url"] == url

    assert webhooks.remove_webhook(url) is True

    loaded = webhooks.load_webhooks()
    assert len(loaded) == 0

@patch("satya.core.webhooks.socket.getaddrinfo")
@patch("satya.core.webhooks.requests.Session")
def test_dispatch(mock_session_cls, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('93.184.216.34', 0))]
    url = "https://example.com/webhook"
    webhooks.add_webhook(url, events=["task_created"])

    webhooks.dispatch("task_created", {"id": "123"})

    import time
    time.sleep(0.1) # Wait for thread

    mock_session_instance = mock_session_cls.return_value
    mock_session_instance.post.assert_called_once()
    args, kwargs = mock_session_instance.post.call_args
    # URL is unmodified, safety is enforced via custom HTTP adapter
    assert args[0] == "https://example.com/webhook"
    assert kwargs["json"] == {"event": "task_created", "payload": {"id": "123"}}
