import sys
import pytest
from unittest.mock import patch, MagicMock

# The conftest mocks are handled before this file
sys.path.insert(0, "src")
from satya.sdk.adapters.otlp import OTLPAdapter

@patch("satya.sdk.adapters.otlp.requests.post")
def test_export_trace(mock_post):
    adapter = OTLPAdapter()
    adapter.export_trace("test_trace_id", "test_agent", "test_event", {"key": "value"})
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "timeout" in kwargs
    assert kwargs["timeout"] == 2

    payload = kwargs["json"]
    assert "resourceSpans" in payload
    spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
    assert spans[0]["name"] == "test_event"

def test_export_log():
    adapter = OTLPAdapter()
    adapter.export_log("test_agent", "test_message", "test_task_id")
