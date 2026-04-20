from sqlalchemy import Column, String, JSON
from ..database import Base

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    team = Column(String, nullable=True)
    model = Column(String, nullable=True)
    environment = Column(String, nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    policies = Column(JSON, nullable=False, default=list)
