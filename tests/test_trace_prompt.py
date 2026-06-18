import pytest
from unittest.mock import MagicMock, patch
from src.satya.sdk.client import SatyaClient

@pytest.fixture
def temp_repo(tmp_path):
    repo_path = str(tmp_path)
    return repo_path

@patch("src.satya.sdk.client.get_agent_key_from_env", return_value="test_key")
@patch("src.satya.sdk.client.require_agent")
def test_trace_prompt(mock_require, mock_get_key, temp_repo):
    mock_adapter = MagicMock()
    client = SatyaClient(agent_name="test_agent", repo_path=temp_repo, adapters=[mock_adapter])

    client.trace_prompt("trace123", "Hello", "World", 10, {"model": "gpt-4"})

    mock_adapter.export_trace.assert_called_once_with(
        "trace123", "test_agent", "prompt_completion",
        {"prompt": "Hello", "response": "World", "tokens_used": 10, "model": "gpt-4"}
    )