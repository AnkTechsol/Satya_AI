import pytest
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langsmith import LangSmithAdapter
import uuid

def test_langsmith_adapter_initialization():
    adapter = LangSmithAdapter(api_key="test_key", project_name="test_project")
    assert adapter.api_key == "test_key"
    assert adapter.project_name == "test_project"
    assert adapter.endpoint == "https://api.smith.langchain.com/runs"

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_langsmith_adapter_export_trace(mock_post):
    adapter = LangSmithAdapter(api_key="test_key", project_name="test_project")

    # Valid UUID trace ID
    trace_id = str(uuid.uuid4())
    data = {"prompt": "test prompt", "response": "test response"}
    adapter.export_trace(trace_id, "test_agent", "prompt_trace", data)

    assert mock_post.called
    call_kwargs = mock_post.call_args[1]
    assert call_kwargs['headers'] == {"x-api-key": "test_key"}
    assert call_kwargs['json']['name'] == "prompt_trace"
    assert call_kwargs['json']['run_type'] == "llm"
    assert call_kwargs['json']['trace_id'] == trace_id
    assert call_kwargs['json']['inputs'] == {"inputs": "test prompt"}
    assert call_kwargs['json']['outputs'] == {"outputs": "test response"}

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_langsmith_adapter_export_trace_invalid_uuid(mock_post):
    adapter = LangSmithAdapter(api_key="test_key")

    # Invalid UUID trace ID should be handled by generating a new one
    trace_id = "unknown"
    data = {"data": "test data"}
    adapter.export_trace(trace_id, "test_agent", "task_created", data)

    assert mock_post.called
    call_kwargs = mock_post.call_args[1]
    assert call_kwargs['json']['name'] == "task_created"
    assert call_kwargs['json']['run_type'] == "chain"
    # Ensure it generated a valid UUID instead of using "unknown"
    assert call_kwargs['json']['trace_id'] != "unknown"
    uuid.UUID(call_kwargs['json']['trace_id'])  # should not raise exception

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_langsmith_adapter_export_trace_no_key(mock_post):
    adapter = LangSmithAdapter(api_key="")
    adapter.export_trace("trace-1", "test_agent", "event", {})
    assert not mock_post.called
