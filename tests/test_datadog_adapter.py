import sys
import pytest
from unittest.mock import patch, MagicMock
import queue

sys.path.insert(0, "src")
from satya.sdk.adapters.datadog import DatadogAdapter

@patch("satya.sdk.adapters.datadog.requests.post")
def test_export_trace(mock_post):
    adapter = DatadogAdapter(api_key="test_key")
    adapter.export_trace("test_trace_id", "test_agent", "test_event", {"key": "value"})
    adapter.queue.join()
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "timeout" in kwargs
    payload = kwargs["json"]
    assert payload[0]["trace_id"] == "test_trace_id"
    assert payload[0]["event_type"] == "test_event"
    adapter.shutdown()

@patch("satya.sdk.adapters.datadog.requests.post")
def test_export_log(mock_post):
    adapter = DatadogAdapter(api_key="test_key")
    adapter.export_log("test_agent", "test_message", "test_task_id")
    adapter.queue.join()
    mock_post.assert_called_once()
    adapter.shutdown()
