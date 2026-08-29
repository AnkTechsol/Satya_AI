import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.datadog import DatadogAdapter

@patch("src.satya.sdk.adapters.datadog.requests.post")
def test_datadog_export_trace(mock_post):
    adapter = DatadogAdapter(api_key="fake-key")
    adapter.export_trace("trace-123", "test_agent", "test_event", {"key": "val"})

    adapter.queue.join()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://http-intake.logs.datadoghq.com/api/v2/logs"
    assert kwargs["headers"]["DD-API-KEY"] == "fake-key"
    assert "trace_data" in kwargs["json"][0]
    assert kwargs["json"][0]["trace_data"]["key"] == "val"
    assert "trace_id:trace-123" in kwargs["json"][0]["ddtags"]

    adapter.shutdown()

@patch("src.satya.sdk.adapters.datadog.requests.post")
def test_datadog_export_log(mock_post):
    adapter = DatadogAdapter(api_key="fake-key")
    adapter.export_log("test_agent", "hello world", "task-1")

    adapter.queue.join()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://http-intake.logs.datadoghq.com/api/v2/logs"
    assert kwargs["headers"]["DD-API-KEY"] == "fake-key"
    assert kwargs["json"][0]["message"] == "hello world"
    assert "task_id:task-1" in kwargs["json"][0]["ddtags"]

    adapter.shutdown()
