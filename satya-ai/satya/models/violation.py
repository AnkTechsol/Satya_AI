from sqlalchemy import Column, String, JSON, Integer, ForeignKey
from ..database import Base

class PolicyViolation(Base):
    __tablename__ = "policy_violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, ForeignKey("audit_events.event_id"), nullable=False, index=True)
    rule_id = Column(String, nullable=False)
    policy_id = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    severity = Column(String, nullable=False)
