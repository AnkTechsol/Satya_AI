import pytest
from src.satya.core.schema import TraceEvent

def test_trace_event_creation():
    event = TraceEvent(
        trace_id="test_trace",
        event_type="test_event",
        agent_name="test_agent",
        data={"key": "value"}
    )

    assert event.trace_id == "test_trace"
    assert event.event_type == "test_event"
    assert event.agent_name == "test_agent"
    assert event.data == {"key": "value"}
    assert "Z" in event.timestamp

def test_trace_event_to_dict():
    event = TraceEvent(
        trace_id="test_trace",
        event_type="test_event",
        agent_name="test_agent",
        data={"key": "value"}
    )

    d = event.to_dict()
    assert d["trace_id"] == "test_trace"
    assert d["event_type"] == "test_event"
    assert d["agent_name"] == "test_agent"
    assert d["data"] == {"key": "value"}
    assert d["timestamp"] == event.timestamp
