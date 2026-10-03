from src.satya.sdk.schema import create_trace_payload

def test_create_trace_payload():
    payload = create_trace_payload("trace123", "task_created", "agent1", {"foo": "bar"})
    assert "timestamp" in payload
    assert payload["trace_id"] == "trace123"
    assert payload["event_type"] == "task_created"
    assert payload["agent_name"] == "agent1"
    assert payload["metadata"] == {"foo": "bar"}