import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.datadog import DatadogAdapter

@patch("src.satya.sdk.adapters.datadog.requests.post")
def test_export_trace(mock_post):
    adapter = DatadogAdapter(api_key="fake-key")
    adapter.export_trace("test_trace_id", "test_agent", "test_event", {"key": "value"})
    adapter.shutdown()
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["DD-API-KEY"] == "fake-key"
    payload = kwargs["json"][0]
    assert payload["message"] == "test_event"
    assert payload["key"] == "value"

def test_export_log():
    adapter = DatadogAdapter(api_key="fake-key")
    adapter.export_log("test_agent", "test_message", "test_task_id")
    adapter.shutdown()
