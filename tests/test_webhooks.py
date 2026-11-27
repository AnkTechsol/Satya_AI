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
def test_dispatch(mock_session_class, mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ('93.184.216.34', 0))]
    url = "https://example.com/webhook"
    webhooks.add_webhook(url, events=["task_created"])

    # Setup the mock session instance
    mock_session_instance = mock_session_class.return_value

    webhooks.dispatch("task_created", {"id": "123"})

    import time
    time.sleep(1.0) # Wait a little longer just in case

    mock_session_instance.post.assert_called_once()
    args, kwargs = mock_session_instance.post.call_args
    assert args[0] == url
    assert kwargs["json"] == {"event": "task_created", "payload": {"id": "123"}}
    assert kwargs["allow_redirects"] is False
