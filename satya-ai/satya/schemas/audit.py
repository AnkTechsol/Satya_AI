from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
from .evaluate import EvaluateViolation

class AuditEventSchema(BaseModel):
    event_id: str
    timestamp: str
    agent_id: str
    decision: Literal["ALLOW", "DENY", "FLAG", "REDACT", "ALERT"]
    matched_policies: List[str] = Field(default_factory=list)
    violations: List[EvaluateViolation] = Field(default_factory=list)
    payload_hash: str
    context_metadata: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float

class AuditQueryFilters(BaseModel):
    agent_id: Optional[str] = None
    decision: Optional[str] = None
    severity: Optional[str] = None
    from_ts: Optional[str] = None
    to_ts: Optional[str] = None
    limit: int = 50
    cursor: Optional[int] = None

class AuditSummary(BaseModel):
    total_events: int
    decisions_breakdown: Dict[str, int]
    top_violating_agents: List[Dict[str, Any]]
