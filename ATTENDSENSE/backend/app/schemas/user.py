from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ── Registration ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    student_id: Optional[str] = None
    full_name:  str
    email:      EmailStr
    password:   str
    role:       Optional[str] = "student"

class RegisterResponse(BaseModel):
    id:         int
    full_name:  str
    email:      str
    role:       str
    created_at: datetime

    class Config:
        from_attributes = True   # Pydantic v2 (use orm_mode=True for v1)

# ── Login ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    full_name:    str