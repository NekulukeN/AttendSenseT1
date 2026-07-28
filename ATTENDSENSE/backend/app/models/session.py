from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class SessionStatus(str, enum.Enum):
    active   = "active"
    ended    = "ended"

class Session(Base):
    __tablename__ = "sessions"

    id          = Column(Integer, primary_key=True, index=True)
    class_name  = Column(String, nullable=False)
    lecturer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_time  = Column(DateTime(timezone=True), server_default=func.now())
    end_time    = Column(DateTime(timezone=True), nullable=True)
    status      = Column(Enum(SessionStatus), default=SessionStatus.active)

    lecturer    = relationship("User", backref="sessions")