from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    student = "student"
    lecturer = "lecturer"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    student_id    = Column(String, unique=True, nullable=True)   # e.g. "S12345"
    full_name     = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role          = Column(Enum(UserRole), default=UserRole.student)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())