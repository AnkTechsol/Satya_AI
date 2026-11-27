import pytest
from unittest.mock import patch
from satya.sdk.adapters.langsmith import LangSmithAdapter
import uuid

def test_langsmith_adapter_export_trace():
    adapter = LangSmithAdapter("test_key", "test_project")

    with patch("satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace(str(uuid.uuid4()), "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert kwargs["headers"] == {"x-api-key": "test_key"}
        assert "timeout" in kwargs

        payload = kwargs["json"]
        assert payload["run_type"] == "chain"
        assert payload["name"] == "test_event"
        assert payload["extra"]["metadata"]["agent_name"] == "test_agent"
        assert payload["extra"]["metadata"]["key"] == "value"
        assert payload["session_name"] == "test_project"

def test_langsmith_adapter_export_trace_with_prompt():
    adapter = LangSmithAdapter("test_key", "test_project")

    with patch("satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace(str(uuid.uuid4()), "test_agent", "test_prompt_event", {"prompt": "What is 2+2?", "response": "4"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        payload = kwargs["json"]
        assert payload["run_type"] == "llm"
        assert payload["inputs"] == {"prompt": "What is 2+2?"}
        assert payload["outputs"] == {"response": "4"}
        assert payload["name"] == "test_prompt_event"

def test_langsmith_adapter_invalid_uuid():
    adapter = LangSmithAdapter("test_key", "test_project")

    with patch("satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("unknown", "test_agent", "test_event", {})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]

        # Verify it generated a valid UUID instead of using "unknown"
        assert payload["id"] != "unknown"
        uuid.UUID(payload["id"]) # Should not raise ValueError

def test_langsmith_adapter_timeout_handling():
    adapter = LangSmithAdapter("test_key", "test_project")

    with patch("satya.sdk.adapters.langsmith.requests.post", side_effect=Exception("Timeout")):
        # Should not raise exception
        adapter.export_trace(str(uuid.uuid4()), "test_agent", "test_event", {"key": "value"})
