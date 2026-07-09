import pytest
from unittest.mock import patch
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

def test_langsmith_adapter_init():
    adapter = LangSmithAdapter(api_key="test_api_key", project_name="test_project")
    assert adapter.api_key == "test_api_key"
    assert adapter.project_name == "test_project"
    assert adapter.host == "https://api.smith.langchain.com"

@patch("src.satya.sdk.adapters.langsmith.requests.post")
def test_langsmith_adapter_export_trace_valid_uuid(mock_post):
    adapter = LangSmithAdapter(api_key="test_api_key", project_name="test_project")
    valid_uuid = "123e4567-e89b-42d3-a456-426614174000"
    data = {"prompt": "Hello", "response": "World"}
    adapter.export_trace(trace_id=valid_uuid, agent_name="test_agent", event_type="test_event", data=data)

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args[1]

    assert call_kwargs["json"]["id"] == valid_uuid
    assert call_kwargs["json"]["run_type"] == "llm"
    assert call_kwargs["json"]["inputs"] == {"prompt": "Hello"}
    assert call_kwargs["json"]["outputs"] == {"response": "World"}
    assert "start_time" in call_kwargs["json"]
    assert "end_time" in call_kwargs["json"]
    assert call_kwargs["headers"] == {"x-api-key": "test_api_key"}

@patch("src.satya.sdk.adapters.langsmith.requests.post")
def test_langsmith_adapter_export_trace_invalid_uuid(mock_post):
    adapter = LangSmithAdapter(api_key="test_api_key", project_name="test_project")
    invalid_uuid = "unknown"
    data = {"prompt": "Hello", "response": "World"}
    adapter.export_trace(trace_id=invalid_uuid, agent_name="test_agent", event_type="test_event", data=data)

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args[1]

    assert call_kwargs["json"]["id"] != invalid_uuid
    import uuid
    # Should not raise exception
    uuid.UUID(call_kwargs["json"]["id"])
