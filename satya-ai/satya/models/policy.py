from sqlalchemy import Column, String, Boolean, JSON
from ..database import Base
import uuid

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=lambda: f"pol_{uuid.uuid4().hex}")
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    rules = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True)
