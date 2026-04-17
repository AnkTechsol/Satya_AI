import pytest
import sys
from unittest.mock import patch, MagicMock
import json

@pytest.fixture(autouse=True)
def unmock_requests():
    """Conftest mocks requests entirely. We need to reset it to a regular MagicMock for our tests."""
    pass

@patch('src.satya.sdk.adapters.otlp.requests.post')
def test_otlp_export_trace(mock_post):
    from src.satya.sdk.adapters.otlp import OTLPAdapter
    adapter = OTLPAdapter()
    adapter.export_trace("12345", "test-agent", "task_created", {"data": "test"})

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs['timeout'] == 2

    payload = kwargs['json']
    assert "resourceSpans" in payload
    spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
    assert len(spans) == 1
    assert spans[0]["name"] == "task_created"

@patch('src.satya.sdk.adapters.otlp.requests.post')
def test_otlp_export_log(mock_post):
    from src.satya.sdk.adapters.otlp import OTLPAdapter
    adapter = OTLPAdapter()
    adapter.export_log("test-agent", "hello world", "task-1")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs['timeout'] == 2

    payload = kwargs['json']
    assert "resourceLogs" in payload
    logs = payload["resourceLogs"][0]["scopeLogs"][0]["logRecords"]
    assert len(logs) == 1
    assert logs[0]["body"]["stringValue"] == "hello world"
