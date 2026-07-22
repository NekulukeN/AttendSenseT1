from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id        = Column(Integer, primary_key=True, index=True)
    actor_id  = Column(Integer, ForeignKey("users.id"), nullable=True)
    action    = Column(String, nullable=False)
    detail    = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    actor = relationship("User", backref="audit_logs")