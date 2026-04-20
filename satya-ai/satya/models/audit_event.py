from sqlalchemy import Column, String, JSON, Float, Integer
from ..database import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    # We use an autoincrement ID as the primary key for the DB, but store event_id
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    decision = Column(String, nullable=False, index=True)
    matched_policies = Column(JSON, nullable=False, default=list)
    violations = Column(JSON, nullable=False, default=list)
    payload_hash = Column(String, nullable=False)
    context_metadata = Column(JSON, nullable=True, default=dict)
    latency_ms = Column(Float, nullable=False)
