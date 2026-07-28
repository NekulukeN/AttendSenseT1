import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.face_profile import FaceProfile
from app.models.session import Session as ClassSession
from app.models.attendance_log import AttendanceLog, AttendanceStatus
from app.utils.jwt import decode_token
from app.utils.face import save_image, generate_embedding, compare_embeddings

router      = APIRouter(prefix="/attendance", tags=["Attendance"])
http_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: DBSession = Depends(get_db)
) -> User:
    token   = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


# ── Create a session (lecturer/admin only) ────────────────────
@router.post("/sessions/create")
def create_session(
    class_name: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Create a new class session."""
    new_session = ClassSession(
        class_name  = class_name,
        lecturer_id = current_user.id,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {
        "message"    : "Session created ✅",
        "session_id" : new_session.id,
        "class_name" : new_session.class_name,
        "status"     : new_session.status,
        "start_time" : new_session.start_time,
    }


# ── Student Check-In ──────────────────────────────────────────
@router.post("/checkin/{session_id}")
def check_in(
    session_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Student checks in by uploading a face photo."""

    # 1. Check session exists and is active
    session = db.query(ClassSession).filter(
        ClassSession.id == session_id,
        ClassSession.status == "active"
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or already ended.")

    # 2. Check not already checked in
    existing = db.query(AttendanceLog).filter(
        AttendanceLog.user_id    == current_user.id,
        AttendanceLog.session_id == session_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in for this session.")

    # 3. Check face profile exists
    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No face profile enrolled. Please enroll first.")

    # 4. Save uploaded photo and generate embedding
    image_path = save_image(file.file, user_id=f"{current_user.id}_checkin")
    try:
        new_embedding = generate_embedding(image_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No face detected. Use a clear photo. ({str(e)})")

    # 5. Compare with stored embedding
    match = compare_embeddings(profile.embedding, new_embedding)
    if not match:
        raise HTTPException(status_code=401, detail="Face does not match. Access denied. ❌")

    # 6. Save attendance record
    log = AttendanceLog(
        user_id    = current_user.id,
        session_id = session_id,
        status     = AttendanceStatus.present,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "message"       : "Check-in successful ✅",
        "user"          : current_user.full_name,
        "session"       : session.class_name,
        "check_in_time" : log.check_in_time,
        "status"        : log.status,
    }


# ── View attendance for a session ─────────────────────────────
@router.get("/sessions/{session_id}/logs")
def get_session_logs(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """View all attendance records for a session."""
    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    return [
        {
            "student"       : log.user.full_name,
            "check_in_time" : log.check_in_time,
            "check_out_time": log.check_out_time,
            "status"        : log.status,
        }
        for log in logs
    ]

# ── Student Check-Out ─────────────────────────────────────────
@router.post("/checkout/{session_id}")
def check_out(
    session_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Student checks out by uploading a face photo."""

    # 1. Find their attendance record
    log = db.query(AttendanceLog).filter(
        AttendanceLog.user_id    == current_user.id,
        AttendanceLog.session_id == session_id
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="No check-in found. You must check in first.")

    if log.check_out_time:
        raise HTTPException(status_code=400, detail="Already checked out.")

    # 2. Check face profile exists
    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No face profile enrolled.")

    # 3. Save uploaded photo and generate embedding
    image_path = save_image(file.file, user_id=f"{current_user.id}_checkout")
    try:
        new_embedding = generate_embedding(image_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No face detected. Use a clear photo. ({str(e)})")

    # 4. Compare with stored embedding
    match = compare_embeddings(profile.embedding, new_embedding)
    if not match:
        raise HTTPException(status_code=401, detail="Face does not match. Access denied. ❌")

    # 5. Record checkout time
    log.check_out_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(log)

    # 6. Calculate duration
    duration = log.check_out_time - log.check_in_time
    minutes  = int(duration.total_seconds() / 60)

    return {
        "message"        : "Check-out successful ✅",
        "user"           : current_user.full_name,
        "session"        : log.session.class_name,
        "check_in_time"  : log.check_in_time,
        "check_out_time" : log.check_out_time,
        "duration_minutes": minutes,
        "status"         : log.status,
    }


# ── End a session (lecturer) ──────────────────────────────────
@router.post("/sessions/{session_id}/end")
def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Lecturer ends a class session."""
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.status == "ended":
        raise HTTPException(status_code=400, detail="Session already ended.")

    session.status   = "ended"
    session.end_time = datetime.now(timezone.utc)
    db.commit()

    return {
        "message"   : "Session ended ✅",
        "session_id": session_id,
        "class_name": session.class_name,
        "end_time"  : session.end_time,
    }

@router.get("/sessions/all")
def get_all_sessions(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get all sessions."""
    sessions = db.query(ClassSession).order_by(ClassSession.start_time.desc()).all()
    return [
        {
            "id"        : s.id,
            "class_name": s.class_name,
            "status"    : s.status,
            "start_time": s.start_time,
            "end_time"  : s.end_time,
        }
        for s in sessions
    ]