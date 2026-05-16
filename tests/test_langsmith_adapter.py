import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langsmith import LangSmithAdapter
import uuid

def test_langsmith_adapter_export_trace():
    adapter = LangSmithAdapter("test_api_key", "test_project")

    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("12345678-1234-5678-1234-567812345678", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert kwargs["headers"]["x-api-key"] == "test_api_key"
        assert "timeout" in kwargs

        payload = kwargs["json"]
        assert payload["id"] == "12345678-1234-5678-1234-567812345678"
        assert payload["name"] == "test_event"
        assert payload["extra"]["metadata"]["agent_name"] == "test_agent"
        assert payload["extra"]["metadata"]["key"] == "value"

def test_langsmith_adapter_timeout_handling():
    adapter = LangSmithAdapter("test_api_key", "test_project")

    with patch("src.satya.sdk.adapters.langsmith.requests.post", side_effect=Exception("Timeout")):
        # Should not raise exception
        adapter.export_trace("12345678-1234-5678-1234-567812345678", "test_agent", "test_event", {"key": "value"})

def test_langsmith_adapter_invalid_uuid():
    adapter = LangSmithAdapter("test_api_key", "test_project")

    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("invalid-uuid", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        payload = kwargs["json"]
        # Ensure a valid uuid is generated if trace id is not valid
        assert uuid.UUID(payload["id"])

def test_langsmith_adapter_export_log():
    adapter = LangSmithAdapter("test_api_key", "test_project")
    adapter.export_log("test_agent", "test_message", "test_task_id")
