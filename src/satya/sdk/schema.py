from typing import TypedDict, Dict, Any
from datetime import datetime, timezone

class TracePayload(TypedDict):
    timestamp: str
    trace_id: str
    event_type: str
    agent_name: str
    metadata: Dict[str, Any]

def create_trace_payload(trace_id: str, event_type: str, agent_name: str, metadata: Dict[str, Any]) -> TracePayload:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "trace_id": trace_id,
        "event_type": event_type,
        "agent_name": agent_name,
        "metadata": metadata
    }