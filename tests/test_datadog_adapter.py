import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, "src")
from satya.sdk.adapters.datadog import DatadogAdapter

@patch("satya.sdk.adapters.datadog.requests.post")
def test_datadog_adapter_export(mock_post):
    adapter = DatadogAdapter(api_key="fake-key")

    adapter.export_trace("trace-1", "agent-x", "task_created", {"status": "ok"})
    adapter.export_log("agent-x", "hello world", "task-1")

    adapter.queue.join()
    adapter.shutdown()

    assert mock_post.call_count == 2