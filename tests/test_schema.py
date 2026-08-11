import json
from src.satya.sdk.schema import TraceEvent, LogEvent

def test_trace_event_serialization():
    event = TraceEvent(trace_id="123", agent_name="test_agent", event_type="test_event", data={"key": "value"})
    assert event.to_dict() == {"trace_id": "123", "agent_name": "test_agent", "event_type": "test_event", "data": {"key": "value"}}
    assert json.loads(event.to_json()) == {"trace_id": "123", "agent_name": "test_agent", "event_type": "test_event", "data": {"key": "value"}}

def test_log_event_serialization():
    event = LogEvent(agent_name="test_agent", message="test message", task_id="task_123")
    assert event.to_dict() == {"agent_name": "test_agent", "message": "test message", "task_id": "task_123"}
    assert json.loads(event.to_json()) == {"agent_name": "test_agent", "message": "test message", "task_id": "task_123"}
