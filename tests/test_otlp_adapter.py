import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.otlp import OTLPAdapter
import src.satya.sdk.adapters.otlp

def test_otlp_adapter_export_trace():
    adapter = OTLPAdapter()

    with patch.object(src.satya.sdk.adapters.otlp.requests, 'post') as mock_post:
        adapter.export_trace("trace-1", "agent-1", "task_created", {"data": "test"})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['timeout'] == 2
        payload = kwargs['json']
        assert "resourceSpans" in payload
        assert payload["resourceSpans"][0]["resource"]["attributes"][0]["value"]["stringValue"] == "agent-1"

def test_otlp_adapter_export_log():
    adapter = OTLPAdapter()

    with patch.object(src.satya.sdk.adapters.otlp.requests, 'post') as mock_post:
        adapter.export_log("agent-1", "hello world", "task-1")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['timeout'] == 2
        payload = kwargs['json']
        assert "resourceLogs" in payload
        assert payload["resourceLogs"][0]["scopeLogs"][0]["logRecords"][0]["body"]["stringValue"] == "hello world"

def test_otlp_adapter_exception_handling(capsys):
    adapter = OTLPAdapter()
    with patch.object(src.satya.sdk.adapters.otlp.requests, 'post', side_effect=Exception("Connection Error")):
        adapter.export_trace("trace-1", "agent-1", "task_created", {"data": "test"})
        adapter.export_log("agent-1", "hello world", "task-1")

    captured = capsys.readouterr()
    assert "[OTLPAdapter Error] Failed to export trace: Connection Error" in captured.out
    assert "[OTLPAdapter Error] Failed to export log: Connection Error" in captured.out
