import pytest
import uuid
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters.langsmith import LangSmithAdapter

def test_langsmith_adapter_initialization():
    adapter = LangSmithAdapter(api_key="test_key", endpoint="https://api.test.com/")
    assert adapter.api_key == "test_key"
    assert adapter.endpoint == "https://api.test.com"

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_export_trace_valid(mock_post):
    adapter = LangSmithAdapter(api_key="test_key")
    trace_id = str(uuid.uuid4())
    data = {"prompt": "hello", "response": "world"}

    adapter.export_trace(trace_id, "test_agent", "test_event", data)

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs['headers']['x-api-key'] == "test_key"

    payload = kwargs['json']
    assert payload['id'] == trace_id
    assert payload['name'] == "test_event"
    assert payload['run_type'] == "llm"
    assert payload['inputs'] == {"prompt": "hello"}
    assert payload['outputs'] == {"response": "world"}

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_export_trace_invalid_uuid(mock_post):
    adapter = LangSmithAdapter(api_key="test_key")
    trace_id = "invalid-uuid"
    data = {"key": "value"}

    adapter.export_trace(trace_id, "test_agent", "test_event", data)

    mock_post.assert_called_once()
    payload = mock_post.call_args[1]['json']
    # Should have generated a valid UUID since the input was invalid
    assert uuid.UUID(payload['id'])
    assert payload['id'] != "invalid-uuid"
    assert payload['run_type'] == "chain"
    assert payload['inputs'] == {}
    assert payload['outputs'] == {}

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_export_trace_no_api_key(mock_post):
    adapter = LangSmithAdapter(api_key="")
    adapter.export_trace("trace", "agent", "event", {})
    mock_post.assert_not_called()

@patch('src.satya.sdk.adapters.langsmith.requests.post')
def test_export_trace_request_exception(mock_post):
    # Should not raise exception
    mock_post.side_effect = Exception("Network error")
    adapter = LangSmithAdapter(api_key="test_key")
    adapter.export_trace(str(uuid.uuid4()), "agent", "event", {})
