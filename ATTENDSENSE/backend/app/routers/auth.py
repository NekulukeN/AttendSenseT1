from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse
from app.models.audit_log import AuditLog
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
http_bearer = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    if payload.student_id:
        dup = db.query(User).filter(User.student_id == payload.student_id).first()
        if dup:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student ID already in use.")

    new_user = User(
        student_id    = payload.student_id,
        full_name     = payload.full_name,
        email         = payload.email,
        password_hash = hash_password(payload.password),
        role          = payload.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    audit = AuditLog(actor_id=new_user.id, action="USER_REGISTERED", detail=f"{new_user.email} registered.")
    db.add(audit)
    db.commit()
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive a JWT access token."""

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    audit = AuditLog(actor_id=user.id, action="USER_LOGIN", detail=f"{user.email} logged in.")
    db.add(audit)
    db.commit()

    return TokenResponse(
        access_token = token,
        token_type   = "bearer",
        role         = user.role,
        full_name    = user.full_name,
    )

@router.get("/me", tags=["Authentication"])
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
):
    """Get current logged-in user profile."""

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role}