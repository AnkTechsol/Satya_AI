from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class RuleSchema(BaseModel):
    rule_id: Optional[str] = Field(default=None, description="Auto-generated if not provided")
    condition: Literal["contains_keyword", "exceeds_token_estimate", "missing_field", "agent_not_registered", "custom_regex"]
    action: Literal["ALLOW", "DENY", "FLAG", "REDACT", "ALERT"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    message: str

    # Specific rule parameters
    pattern: Optional[str] = None
    field: Optional[str] = None
    keywords: Optional[List[str]] = None
    threshold: Optional[int] = None

class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[RuleSchema] = Field(default_factory=list)
    is_active: bool = True

class PolicyRead(PolicyCreate):
    id: str

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[RuleSchema]] = None
    is_active: Optional[bool] = None
