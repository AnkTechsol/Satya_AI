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

    mock_session_cls.return_value.post.assert_called_once()
    args, kwargs = mock_session_cls.return_value.post.call_args
    assert args[0] == url
    assert kwargs["json"] == {"event": "task_created", "payload": {"id": "123"}}

    # Verify the HostHeaderSSLAdapter was properly mounted with the correct IP
    mount_calls = mock_session_cls.return_value.mount.call_args_list
    assert len(mount_calls) == 2
    assert mount_calls[0][0][0] == "http://"
    assert mount_calls[0][0][1].target_ip == "93.184.216.34"
    assert mount_calls[1][0][0] == "https://"
    assert mount_calls[1][0][1].target_ip == "93.184.216.34"
