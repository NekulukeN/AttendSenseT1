from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.probe_result import ProbeResult
from app.models.attendance_log import AttendanceLog
from app.models.anomaly_log import AnomalyLog
from app.utils.jwt import decode_token
from app.utils.liveness import analyze_liveness

router      = APIRouter(prefix="/probe", tags=["Random Probe Engine"])
http_bearer = HTTPBearer()


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
        "has_probe"  : True,
        "probe_id"   : probe.id,
        "action"     : probe.probe_type,
        "message"    : f"Please perform: {probe.probe_type.replace('_', ' ').upper()}",
        "issued_at"  : probe.sent_time,
    }


@router.post("/respond/{probe_id}")
async def respond_to_probe(
    probe_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Student responds to a probe by uploading a photo of the action."""

    # Find the probe
    probe = db.query(ProbeResult).filter(
        ProbeResult.id      == probe_id,
        ProbeResult.user_id == current_user.id,
        ProbeResult.status  == "pending"
    ).first()

    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found or already answered.")

    # Read and analyze image
    image_bytes = await file.read()
    analysis    = analyze_liveness(image_bytes)

    if not analysis.get("face_detected"):
        raise HTTPException(status_code=422, detail="No face detected in image.")

    # Check if correct action was performed
    passed = False
    action = probe.probe_type

    if action == "blink":
        passed = analysis["eyes_closed"]
    elif action == "smile":
        passed = analysis["smiling"]
    elif action == "turn_left":
        passed = analysis["head_direction"] == "left"
    elif action == "turn_right":
        passed = analysis["head_direction"] == "right"

    # Update probe record
    probe.status        = "passed" if passed else "failed"
    probe.passed        = passed
    probe.response_time = datetime.now(timezone.utc)

    # Log anomaly if failed
    if not passed:
        anomaly = AnomalyLog(
            user_id    = current_user.id,
            session_id = probe.session_id,
            reason     = f"Probe '{action}' failed — incorrect response.",
        )
        db.add(anomaly)

    db.commit()

    return {
        "probe_id" : probe_id,
        "action"   : action,
        "passed"   : passed,
        "message"  : f"Probe {'passed ✅' if passed else 'failed ❌'}",
    }


@router.post("/issue-manual/{session_id}")
def issue_manual_probe(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Manually issue probes to all currently checked-in students in a session,
    for testing purposes. In production the scheduler does this automatically.
    """
    import random

    checked_in = db.query(AttendanceLog).filter(
        AttendanceLog.session_id == session_id,
        AttendanceLog.check_out_time == None
    ).all()

    if not checked_in:
        raise HTTPException(status_code=404, detail="No checked-in students in this session.")

    PROBE_ACTIONS = ["blink", "smile", "turn_left", "turn_right"]
    issued = []

    for log in checked_in:
        action = random.choice(PROBE_ACTIONS)
        probe = ProbeResult(
            user_id    = log.user_id,
            session_id = session_id,
            probe_type = action,
            status     = "pending",
        )
        db.add(probe)
        db.flush()  # so probe.id is available before commit
        issued.append({
            "user_id"  : log.user_id,
            "probe_id" : probe.id,
            "action"   : action
        })

    db.commit()

    return {
        "message": f"Probes issued to {len(issued)} student(s) ✅",
        "issued" : issued
    }


@router.get("/anomalies/{session_id}")
def get_anomalies(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """View all anomalies for a session (lecturer/admin)."""
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