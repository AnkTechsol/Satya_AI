import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.datadog import DatadogAdapter
import uuid

def test_datadog_adapter_export_trace():
    adapter = DatadogAdapter(api_key="test_key")

    with patch("src.satya.sdk.adapters.datadog.requests.post") as mock_post:
        adapter.export_trace("test_trace", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert kwargs["headers"]["DD-API-KEY"] == "test_key"
        assert "timeout" in kwargs

        payload = kwargs["json"][0]
        assert payload["ddsource"] == "satya_agent"
        assert "agent:test_agent" in payload["ddtags"]
        assert "event_type:test_event" in payload["ddtags"]

def test_datadog_adapter_export_log():
    adapter = DatadogAdapter(api_key="test_key")

    with patch("src.satya.sdk.adapters.datadog.requests.post") as mock_post:
        adapter.export_log("test_agent", "test message", "test_task")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        payload = kwargs["json"][0]
        assert payload["ddsource"] == "satya_agent"
        assert "agent:test_agent" in payload["ddtags"]

def test_datadog_adapter_missing_key(monkeypatch):
    monkeypatch.delenv("DATADOG_API_KEY", raising=False)
    with pytest.raises(ValueError):
        DatadogAdapter()
