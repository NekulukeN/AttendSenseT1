from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ProbeResult(Base):
    __tablename__ = "probe_results"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id    = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    probe_type    = Column(String, nullable=False)   # blink, smile, turn_left, turn_right
    status        = Column(String, default="pending") # pending, passed, failed, expired
    sent_time     = Column(DateTime(timezone=True), server_default=func.now())
    response_time = Column(DateTime(timezone=True), nullable=True)
    passed        = Column(Boolean, default=False)

    user    = relationship("User", backref="probe_results")
    session = relationship("Session", backref="probe_results")