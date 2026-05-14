import pytest
import os
from unittest.mock import patch, MagicMock
from src.satya.sdk.adapters import ConsoleAdapter, OTLPAdapter
from src.satya.sdk.client import SatyaClient

@patch('src.satya.sdk.client.require_agent')
@patch('src.satya.sdk.client.get_agent_key_from_env')
def test_adapters_initialization(mock_get_key, mock_require_agent):
    mock_get_key.return_value = "mock_key"
    mock_require_agent.return_value = True

    console_adapter = ConsoleAdapter()
    otlp_adapter = OTLPAdapter()

    # Use a dummy client to avoid directory access issues
    with patch('src.satya.sdk.client.storage.ensure_satya_dirs'):
        with patch('src.satya.sdk.client.GitHandler'):
            client = SatyaClient(agent_name="test_agent", repo_path="/tmp", adapters=[console_adapter, otlp_adapter])
            assert len(client.adapters) == 2

def test_console_adapter_methods(capsys):
    adapter = ConsoleAdapter()
    adapter.export_trace("trace-1", "agent-1", "task_created", {"data": "test"})
    captured = capsys.readouterr()
    assert "[ConsoleAdapter] Trace trace-1 | Agent: agent-1" in captured.out

    adapter.export_log("agent-1", "hello world", "task-1")
    captured = capsys.readouterr()
    assert "[ConsoleAdapter] Log | Agent: agent-1 | Task: task-1 | Message: hello world" in captured.out

@patch('src.satya.sdk.client.require_agent')
@patch('src.satya.sdk.client.get_agent_key_from_env')
def test_trace_prompt_with_adapters(mock_get_key, mock_require_agent):
    mock_get_key.return_value = "mock_key"
    mock_require_agent.return_value = True

    mock_adapter = MagicMock()

    with patch('src.satya.sdk.client.storage.ensure_satya_dirs'):
        with patch('src.satya.sdk.client.GitHandler'):
            client = SatyaClient(agent_name="test_agent", repo_path="/tmp", adapters=[mock_adapter])

            client.trace_prompt("trace-1", "test prompt", "test response", tokens_used=100, model="gpt-4")

            mock_adapter.export_trace.assert_called_once_with(
                "trace-1",
                "test_agent",
                "prompt_generation",
                {
                    "prompt": "test prompt",
                    "response": "test response",
                    "tokens_used": 100,
                    "model": "gpt-4"
                }
            )
