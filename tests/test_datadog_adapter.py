import pytest
import json
from unittest.mock import patch, MagicMock
import queue
import os
import sys
sys.path.insert(0, os.path.abspath("src"))

from satya.sdk.adapters.datadog import DatadogAdapter

@patch('satya.sdk.adapters.datadog.requests.post')
def test_datadog_adapter_trace_and_log(mock_post):
    adapter = DatadogAdapter(api_key="fake-key")

    adapter.export_trace(trace_id="t123", agent_name="test-agent", event_type="test-event", data={"key": "value"})
    adapter.export_log(agent_name="test-agent", message="hello world", task_id="task123")

    adapter.queue.join()
    adapter.shutdown()

    assert mock_post.call_count == 2
    args, kwargs = mock_post.call_args_list[0]
    assert kwargs['headers']['DD-API-KEY'] == 'fake-key'
    assert kwargs['json']['trace_id'] == 't123'
    assert kwargs['json']['key'] == 'value'

    args, kwargs = mock_post.call_args_list[1]
    assert kwargs['json']['message'] == 'hello world'
    assert kwargs['json']['task_id'] == 'task123'
