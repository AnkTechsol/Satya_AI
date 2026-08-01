import pytest
from unittest.mock import patch, MagicMock
from satya.sdk.adapters.otlp import OTLPAdapter
from satya.sdk.adapters.langsmith import LangSmithAdapter
from satya.sdk.adapters.langfuse import LangfuseAdapter
import json

def test_otlp_adapter():
    adapter = OTLPAdapter()
    with patch('satya.sdk.adapters.otlp.requests.post') as mock_post:
        adapter.export_trace("test_trace_123", "test_agent", "test_event", {"key": "val"})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['timeout'] == 2
        payload = kwargs['json']
        assert payload["resourceSpans"][0]["resource"]["attributes"][0]["value"]["stringValue"] == "satya-agent"
        spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
        assert spans[0]["name"] == "test_event"
        assert spans[0]["attributes"][0]["key"] == "key"

def test_langsmith_adapter():
    adapter = LangSmithAdapter("test_key", "test_project")
    with patch('satya.sdk.adapters.langsmith.requests.post') as mock_post:
        adapter.export_trace("12345678-1234-5678-1234-567812345678", "test_agent", "test_event", {"prompt": "hello", "response": "world", "meta": "data"})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['headers']["x-api-key"] == "test_key"
        payload = kwargs['json']
        assert payload["run_type"] == "llm"
        assert payload["inputs"] == {"prompt": "hello"}
        assert payload["outputs"] == {"response": "world"}
        assert payload["extra"]["metadata"]["agent_name"] == "test_agent"
        assert payload["extra"]["metadata"]["meta"] == "data"
        assert "end_time" in payload

def test_langsmith_adapter_chain():
    adapter = LangSmithAdapter("test_key", "test_project")
    with patch('satya.sdk.adapters.langsmith.requests.post') as mock_post:
        adapter.export_trace("12345678-1234-5678-1234-567812345678", "test_agent", "test_event", {"key": "val"})
        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        assert payload["run_type"] == "chain"
        assert payload["inputs"] == {"data": {"key": "val"}}

def test_langfuse_adapter():
    adapter = LangfuseAdapter("pk", "sk")
    with patch('satya.sdk.adapters.langfuse.requests.post') as mock_post:
        adapter.export_trace("trace_123", "test_agent", "test_event", {"key": "val"})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['auth'] == ("pk", "sk")
        payload = kwargs['json']
        assert payload["batch"][0]["body"]["name"] == "test_event"
        assert payload["batch"][0]["body"]["metadata"]["agent_name"] == "test_agent"
