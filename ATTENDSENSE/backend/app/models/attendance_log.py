from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AttendanceStatus(str, enum.Enum):
    present  = "present"
    late     = "late"
    absent   = "absent"

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id     = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    check_in_time  = Column(DateTime(timezone=True), server_default=func.now())
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    status         = Column(Enum(AttendanceStatus), default=AttendanceStatus.present)

    user    = relationship("User", backref="attendance_logs")
    session = relationship("Session", backref="attendance_logs")