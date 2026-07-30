import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.probe_result import ProbeResult
from app.models.anomaly_log import AnomalyLog
from app.models.session import Session as ClassSession
from app.models.attendance_log import AttendanceLog
from app.utils.jwt import decode_token
from app.utils.liveness import analyze_liveness

router      = APIRouter(prefix="/probe", tags=["Random Probe Engine"])
http_bearer = HTTPBearer()

PROBE_IMAGE_DIR = "uploads/probes"
os.makedirs(PROBE_IMAGE_DIR, exist_ok=True)

PROBE_ACTIONS = ["blink", "smile", "turn_left", "turn_right"]  # slide_check removed — now attached to all


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: DBSession = Depends(get_db)
) -> User:
    token   = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token.")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/pending")
def get_pending_probe(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Student polls this to check if they have a pending probe challenge."""
    probe = db.query(ProbeResult).filter(
        ProbeResult.user_id == current_user.id,
        ProbeResult.status  == "pending"
    ).order_by(ProbeResult.sent_time.desc()).first()

    if not probe:
        return {"has_probe": False, "message": "No pending probe."}

    return {
        "has_probe" : True,
        "probe_id"  : probe.id,
        "action"    : probe.probe_type,
        "message"   : f"Please perform: {probe.probe_type.replace('_', ' ').upper()} and enter the current slide number.",
        "issued_at" : probe.sent_time,
    }


@router.post("/respond/{probe_id}")
async def respond_to_probe(
    probe_id: int,
    slide_number: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Student responds to a probe with BOTH a photo (liveness action) AND the current slide number."""

    probe = db.query(ProbeResult).filter(
        ProbeResult.id      == probe_id,
        ProbeResult.user_id == current_user.id,
        ProbeResult.status  == "pending"
    ).first()

    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found or already answered.")

    image_bytes = await file.read()

    image_path = f"{PROBE_IMAGE_DIR}/probe_{probe_id}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    probe.image_path = image_path

    # Slide check — evaluated first, doesn't need image analysis
    probe.slide_answer = slide_number
    slide_passed        = (slide_number == probe.expected_slide)
    probe.slide_passed  = slide_passed

    analysis = analyze_liveness(image_bytes)

    if not analysis.get("face_detected"):
        probe.status        = "failed"
        probe.passed        = False
        probe.camera_passed = False   # NEW — explicitly set even on this early-exit path
        probe.response_time = datetime.now(timezone.utc)
        anomaly = AnomalyLog(
            user_id    = current_user.id,
            session_id = probe.session_id,
            reason     = "Probe failed — no face detected in submitted image.",
        )
        db.add(anomaly)
        db.commit()
        raise HTTPException(status_code=422, detail="No face detected in image.")

    action = probe.probe_type
    camera_passed = False   # calculated here, in every remaining code path

    if action == "blink":
        camera_passed = analysis["eyes_closed"]
    elif action == "smile":
        camera_passed = analysis["smiling"]
    elif action == "turn_left":
        camera_passed = analysis["head_direction"] == "left"
    elif action == "turn_right":
        camera_passed = analysis["head_direction"] == "right"

    probe.camera_passed = camera_passed   # ← moved here, AFTER camera_passed is computed

    overall_passed = camera_passed and slide_passed

    probe.status        = "passed" if overall_passed else "failed"
    probe.passed        = overall_passed
    probe.response_time = datetime.now(timezone.utc)

    if not overall_passed:
        reasons = []
        if not camera_passed:
            reasons.append(f"liveness action '{action}' failed")
        if not slide_passed:
            reasons.append(f"slide answer {slide_number} incorrect (expected {probe.expected_slide})")
        anomaly = AnomalyLog(
            user_id    = current_user.id,
            session_id = probe.session_id,
            reason     = "Probe failed — " + "; ".join(reasons),
        )
        db.add(anomaly)

    db.commit()

    return {
        "probe_id"      : probe_id,
        "action"        : action,
        "camera_passed" : camera_passed,
        "slide_passed"  : slide_passed,
        "passed"        : overall_passed,
        "message"       : f"Probe {'passed ✅' if overall_passed else 'failed ❌'}",
    }


@router.post("/issue-manual/{session_id}")
def issue_manual_probe(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Manually issue probes to all currently checked-in students, for testing."""
    import random

    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    checked_in = db.query(AttendanceLog).filter(
        AttendanceLog.session_id == session_id,
        AttendanceLog.check_out_time == None
    ).all()

    if not checked_in:
        raise HTTPException(status_code=404, detail="No checked-in students in this session.")

    issued = []
    for log in checked_in:
        action = random.choice(PROBE_ACTIONS)
        probe = ProbeResult(
            user_id        = log.user_id,
            session_id     = session_id,
            probe_type     = action,
            status         = "pending",
            expected_slide = session.current_slide,   # NEW — snapshot at issue time
        )
        db.add(probe)
        db.flush()
        issued.append({
            "user_id"       : log.user_id,
            "probe_id"      : probe.id,
            "action"        : action,
            "expected_slide": session.current_slide
        })

    db.commit()

    return {
        "message": f"Probes issued to {len(issued)} student(s) ✅",
        "issued" : issued
    }


@router.get("/image/{probe_id}")
def get_probe_image(
    probe_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    probe = db.query(ProbeResult).filter(ProbeResult.id == probe_id).first()
    if not probe or not probe.image_path or not os.path.exists(probe.image_path):
        raise HTTPException(status_code=404, detail="No image available for this probe.")
    return FileResponse(probe.image_path)


@router.get("/results/{session_id}")
def get_probe_results(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Lecturer dashboard: full probe history for a session."""
    probes = db.query(ProbeResult).filter(ProbeResult.session_id == session_id).all()

    return [
        {
            "probe_id"      : p.id,
            "student"       : p.user.full_name,
            "action"        : p.probe_type,
            "status"        : p.status,
            "camera_passed" : p.passed if p.slide_passed is None else (p.passed or p.slide_passed) and p.passed is not None,
            "slide_passed"  : p.slide_passed,
            "expected_slide": p.expected_slide,
            "slide_answer"  : p.slide_answer,
            "sent_time"     : p.sent_time,
            "response_time" : p.response_time,
            "has_image"     : p.image_path is not None,
            "image_url"     : f"/probe/image/{p.id}" if p.image_path else None,
        }
        for p in probes
    ]


@router.get("/anomalies/{session_id}")
def get_anomalies(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    anomalies = db.query(AnomalyLog).filter(
        AnomalyLog.session_id == session_id
    ).all()

    return [
        {
            "student"   : a.user.full_name,
            "reason"    : a.reason,
            "flagged_at": a.created_at,
        }
        for a in anomalies
    ]