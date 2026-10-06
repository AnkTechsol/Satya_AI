import os
import json
import pytest
from src.satya.sdk import init
from unittest.mock import patch, MagicMock

@patch('src.satya.core.storage.save_json')
def test_log_llm_completion(mock_save_json, monkeypatch):
    monkeypatch.setenv('SATYA_AGENT_KEY', 'test-key')
    monkeypatch.setenv('SATYA_AGENT_KEYS', 'test-key')

    # Reload auth module to pick up new env vars
    import importlib
    import src.satya.auth as auth
    importlib.reload(auth)

    client = init("test_agent")

    adapter_mock = MagicMock()
    client.adapters = [adapter_mock]

    client.log_llm_completion("hello", "world", 10, "gpt-4")

    mock_save_json.assert_called_once()
    args, kwargs = mock_save_json.call_args
    assert "prompts" in args[0]
    assert args[1]["prompt"] == "hello"
    assert args[1]["response"] == "world"
    assert args[1]["tokens"] == 10

    adapter_mock.export_trace.assert_called_once()