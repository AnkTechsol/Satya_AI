import pytest
from unittest.mock import MagicMock, patch
from src.satya.sdk.client import SatyaClient

@patch('src.satya.sdk.client.require_agent')
@patch('src.satya.sdk.client.storage.ensure_satya_dirs')
@patch('src.satya.sdk.client.GitHandler')
def test_adapter_integration(mock_git, mock_dirs, mock_req_agent, tmp_path):
    mock_req_agent.return_value = True

    # Create a mock adapter
    mock_adapter = MagicMock()

    # Initialize client with the mock adapter
    client = SatyaClient(agent_name="test_agent", repo_path=str(tmp_path), adapters=[mock_adapter])

    # Mock task creation internals to just test the adapter call
    with patch.object(client.tasks, 'create_task', return_value={"id": "task1", "trace_id": "trace1", "title": "Test"}):
        with patch('src.satya.sdk.client.append_audit_event'):
            client.create_task("Test Task", "This is a test description longer than 10 chars")

    # Check if adapter.export_trace was called for task creation
    mock_adapter.export_trace.assert_any_call("trace1", "test_agent", "task_created", {"task_id": "task1", "title": "Test Task"})

    # Test log
    client.current_task = {"id": "task1"}
    with patch.object(client.tasks, 'add_comment'):
        with patch('builtins.open'):
            client.log("Test log message")

    # Check if adapter.export_log was called
    mock_adapter.export_log.assert_called_with("test_agent", "Test log message", "task1")
