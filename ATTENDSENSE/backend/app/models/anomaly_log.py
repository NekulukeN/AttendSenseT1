from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    reason     = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user    = relationship("User", backref="anomaly_logs")
    session = relationship("Session", backref="anomaly_logs")