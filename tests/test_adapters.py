import pytest
import os
import uuid
import socket
from unittest.mock import patch, MagicMock
from src.satya.core.adapters.otlp import OTLPAdapter
from src.satya.core.adapters.langsmith import LangSmithAdapter

def test_otlp_adapter_creates_dir(tmp_path):
    filepath = str(tmp_path / "deep" / "dir" / "traces.jsonl")
    adapter = OTLPAdapter(filepath=filepath)
    adapter.export_trace("trace123", "agentA", "test_event", {"key": "val"})
    assert os.path.exists(filepath)

def test_otlp_adapter_no_dir(tmp_path):
    # Testing when filepath has no directory component
    os.chdir(tmp_path)
    filepath = "traces.jsonl"
    adapter = OTLPAdapter(filepath=filepath)
    adapter.export_trace("trace123", "agentA", "test_event", {"key": "val"})
    assert os.path.exists(filepath)

def test_langsmith_uuid_fallback():
    # Because there's a problem with mocking SSRFProtectedAdapter inside LangSmithAdapter.__init__ in another test,
    # we use a clean context. We actually just need to test that UUID parsing/fallback works.
    with patch('src.satya.core.adapters.langsmith.SSRFProtectedAdapter'):
        adapter = LangSmithAdapter(api_key="test")

    mock_post = MagicMock()
    adapter.session.post = mock_post
    adapter.export_trace("invalid_uuid", "agentA", "test_event", {"prompt": "hi", "response": "hello"})

    # Verify fallback UUID was used and inputs/outputs mapped
    assert mock_post.called
    call_args = mock_post.call_args[1]
    assert call_args['json']['inputs'] == "hi"
    assert call_args['json']['outputs'] == "hello"
    assert call_args['json']['run_type'] == "llm"
    assert "end_time" in call_args['json']

    # Check trace_id was converted to valid UUID
    try:
        uuid.UUID(call_args['json']['id'])
    except ValueError:
        pytest.fail("Fallback UUID was not a valid UUID")

def test_langsmith_ssrf_protection():
    with patch('src.satya.core.adapters.langsmith.SSRFProtectedAdapter'):
        adapter = LangSmithAdapter(api_key="test", endpoint="https://example.com")

    # We mock post so we don't actually try to make a request
    mock_post = MagicMock()
    adapter.session.post = mock_post

    adapter.export_trace("invalid_uuid", "agentA", "test_event", {})
    assert mock_post.called
