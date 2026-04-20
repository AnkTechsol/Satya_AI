from pydantic import BaseModel, Field
from typing import List, Optional

class AgentCreate(BaseModel):
    agent_id: str
    name: str
    description: Optional[str] = None
    team: Optional[str] = None
    model: Optional[str] = None
    environment: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    policies: List[str] = Field(default_factory=list)

class AgentRead(AgentCreate):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    team: Optional[str] = None
    model: Optional[str] = None
    environment: Optional[str] = None
    tags: Optional[List[str]] = None
    policies: Optional[List[str]] = None
