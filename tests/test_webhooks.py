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

def test_add_and_remove_webhook():
    url = "https://example.com/webhook"

    assert webhooks.add_webhook(url) is True

    loaded = webhooks.load_webhooks()
    assert len(loaded) == 1
    assert loaded[0]["url"] == url

    assert webhooks.remove_webhook(url) is True

    loaded = webhooks.load_webhooks()
    assert len(loaded) == 0

@patch("satya.core.webhooks.requests.post")
def test_dispatch(mock_post):
    url = "https://example.com/webhook"
    webhooks.add_webhook(url, events=["task_created"])

    webhooks.dispatch("task_created", {"id": "123"})

    import time
    time.sleep(0.1) # Wait for thread

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == url
    assert kwargs["json"] == {"event": "task_created", "payload": {"id": "123"}}
