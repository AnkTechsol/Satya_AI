import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath("src"))
from satya.sdk.adapters.langsmith import LangSmithAdapter
import json

def test_langsmith_adapter_export_trace():
    adapter = LangSmithAdapter(api_key="test_api_key", project_name="test_project")

    with patch("src.satya.sdk.adapters.langsmith.requests.post") as mock_post:
        adapter.export_trace("12345678-1234-5678-1234-567812345678", "test_agent", "test_event", {"key": "value"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        assert kwargs["headers"] == {"x-api-key": "test_api_key"}
        assert "timeout" in kwargs
        assert kwargs["timeout"] == 2

        payload = kwargs["json"]
        assert payload["id"] == "12345678-1234-5678-1234-567812345678"
        assert payload["name"] == "test_event"
        assert payload["run_type"] == "tool"
        assert payload["session_name"] == "test_project"
        assert payload["extra"]["metadata"]["agent_name"] == "test_agent"
        assert payload["extra"]["metadata"]["key"] == "value"

def test_langsmith_adapter_timeout_handling():
    adapter = LangSmithAdapter("test_api_key")

    with patch("src.satya.sdk.adapters.langsmith.requests.post", side_effect=Exception("Timeout")):
        # Should not raise exception
        adapter.export_trace("trace123", "test_agent", "test_event", {"key": "value"})