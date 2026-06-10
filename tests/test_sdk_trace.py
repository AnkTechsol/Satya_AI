import sys
import os
sys.path.insert(0, os.path.abspath("src"))
import pytest
from unittest.mock import MagicMock
import satya.core.storage as storage
from src.satya.sdk.client import SatyaClient
from importlib import reload
import src.satya.auth as auth
import os

@pytest.fixture
def temp_client_with_adapters(monkeypatch, tmp_path):
    monkeypatch.setenv("SATYA_AGENT_KEYS", "DEMO_KEY")
    reload(auth)

    repo_path = str(tmp_path)
    storage.SATYA_DIR = os.path.join(repo_path, "satya_data")
    storage.TASKS_DIR = os.path.join(storage.SATYA_DIR, "tasks")
    storage.TRUTH_DIR = os.path.join(storage.SATYA_DIR, "truth")
    storage.AGENTS_DIR = os.path.join(storage.SATYA_DIR, "agents")

    adapter_mock = MagicMock()
    client = SatyaClient(agent_name="test_agent", repo_path=repo_path, adapters=[adapter_mock])
    yield client, adapter_mock

def test_trace_prompt(temp_client_with_adapters):
    client, adapter_mock = temp_client_with_adapters
    prompt = "Hello AI"
    response = "Hello User"
    metadata = {"tokens": 10}

    client.trace_prompt(prompt, response, metadata)

    # Assert adapter was called
    adapter_mock.export_trace.assert_called_once()
    args, kwargs = adapter_mock.export_trace.call_args
    assert args[0] == "unknown" # trace_id
    assert args[1] == "test_agent" # agent_name
    assert args[2] == "prompt_trace" # event_type
    assert args[3]["prompt"] == prompt
    assert args[3]["response"] == response
    assert args[3]["tokens"] == 10
