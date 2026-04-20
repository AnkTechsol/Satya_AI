from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal

class EvaluateRequest(BaseModel):
    agent_id: str
    payload: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class EvaluateViolation(BaseModel):
    rule_id: str
    policy_id: str
    reason: str
    severity: str

class EvaluateResult(BaseModel):
    decision: Literal["ALLOW", "DENY", "FLAG", "REDACT", "ALERT"]
    event_id: str
    latency_ms: float
    matched_policies: List[str] = Field(default_factory=list)
    violations: Optional[List[EvaluateViolation]] = None
    redacted_fields: Optional[List[str]] = None
    payload: Optional[Dict[str, Any]] = None
