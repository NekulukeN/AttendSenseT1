import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.session import Session as ClassSession
from app.models.attendance_log import AttendanceLog
from app.models.probe_result import ProbeResult
from app.models.anomaly_log import AnomalyLog
from app.utils.jwt import decode_token

router      = APIRouter(prefix="/reports", tags=["Reports"])
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


# ── Session Summary ───────────────────────────────────────────
@router.get("/sessions/{session_id}/summary")
def session_summary(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Full attendance summary for a session."""

    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    logs      = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    probes    = db.query(ProbeResult).filter(ProbeResult.session_id == session_id).all()
    anomalies = db.query(AnomalyLog).filter(AnomalyLog.session_id == session_id).all()

    total_present  = len(logs)
    total_checkedout = sum(1 for l in logs if l.check_out_time)
    total_probes   = len(probes)
    probes_passed  = sum(1 for p in probes if p.passed)
    probes_failed  = sum(1 for p in probes if p.status == "failed")
    probes_expired = sum(1 for p in probes if p.status == "expired")

    attendance_records = []
    for log in logs:
        duration = None
        if log.check_out_time:
            duration = int((log.check_out_time - log.check_in_time).total_seconds() / 60)

        # Count probes for this student
        student_probes  = [p for p in probes if p.user_id == log.user_id]
        student_anomalies = [a for a in anomalies if a.user_id == log.user_id]

        attendance_records.append({
            "student_id"      : log.user.student_id,
            "full_name"       : log.user.full_name,
            "check_in_time"   : log.check_in_time,
            "check_out_time"  : log.check_out_time,
            "duration_minutes": duration,
            "status"          : log.status,
            "probes_received" : len(student_probes),
            "probes_passed"   : sum(1 for p in student_probes if p.passed),
            "anomalies"       : len(student_anomalies),
        })

    return {
        "session_id"       : session_id,
        "class_name"       : session.class_name,
        "start_time"       : session.start_time,
        "end_time"         : session.end_time,
        "status"           : session.status,
        "total_present"    : total_present,
        "total_checked_out": total_checkedout,
        "total_probes"     : total_probes,
        "probes_passed"    : probes_passed,
        "probes_failed"    : probes_failed,
        "probes_expired"   : probes_expired,
        "total_anomalies"  : len(anomalies),
        "attendance"       : attendance_records,
    }


# ── Absent List ───────────────────────────────────────────────
@router.get("/sessions/{session_id}/absent")
def absent_list(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """List all enrolled students who did NOT check in."""

    # All students
    all_students = db.query(User).filter(User.role == "student").all()

    # Students who checked in
    checked_in_ids = {
        log.user_id for log in
        db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    }

    absent = [
        {
            "student_id": s.student_id,
            "full_name" : s.full_name,
            "email"     : s.email,
        }
        for s in all_students
        if s.id not in checked_in_ids
    ]

    return {
        "session_id"   : session_id,
        "total_absent" : len(absent),
        "absent_students": absent,
    }


# ── Probe Failures Report ─────────────────────────────────────
@router.get("/sessions/{session_id}/probe-failures")
def probe_failures(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """List all failed and expired probes for a session."""

    failed = db.query(ProbeResult).filter(
        ProbeResult.session_id == session_id,
        ProbeResult.status.in_(["failed", "expired"])
    ).all()

    return {
        "session_id"    : session_id,
        "total_failures": len(failed),
        "failures": [
            {
                "student"      : p.user.full_name,
                "action"       : p.probe_type,
                "status"       : p.status,
                "issued_at"    : p.sent_time,
                "responded_at" : p.response_time,
            }
            for p in failed
        ]
    }


# ── Student Personal Report ───────────────────────────────────
@router.get("/my-attendance")
def my_attendance(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Student views their own attendance history."""

    logs = db.query(AttendanceLog).filter(
        AttendanceLog.user_id == current_user.id
    ).all()

    records = []
    for log in logs:
        duration = None
        if log.check_out_time:
            duration = int((log.check_out_time - log.check_in_time).total_seconds() / 60)

        probes = db.query(ProbeResult).filter(
            ProbeResult.user_id    == current_user.id,
            ProbeResult.session_id == log.session_id
        ).all()

        records.append({
            "class_name"      : log.session.class_name,
            "date"            : log.check_in_time,
            "check_in_time"   : log.check_in_time,
            "check_out_time"  : log.check_out_time,
            "duration_minutes": duration,
            "status"          : log.status,
            "probes_received" : len(probes),
            "probes_passed"   : sum(1 for p in probes if p.passed),
        })

    total     = len(records)
    present   = sum(1 for r in records if r["status"] == "present")
    rate      = round((present / total * 100), 1) if total > 0 else 0

    return {
        "student"          : current_user.full_name,
        "total_sessions"   : total,
        "total_present"    : present,
        "attendance_rate"  : f"{rate}%",
        "records"          : records,
    }


# ── CSV Export ────────────────────────────────────────────────
@router.get("/sessions/{session_id}/export-csv")
def export_csv(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Download attendance report as CSV file."""

    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    logs    = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    probes  = db.query(ProbeResult).filter(ProbeResult.session_id == session_id).all()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Student ID", "Full Name", "Email",
        "Check-In Time", "Check-Out Time", "Duration (mins)",
        "Status", "Probes Received", "Probes Passed", "Probe Pass Rate"
    ])

    # Rows
    for log in logs:
        duration = ""
        if log.check_out_time:
            duration = int((log.check_out_time - log.check_in_time).total_seconds() / 60)

        student_probes = [p for p in probes if p.user_id == log.user_id]
        passed         = sum(1 for p in student_probes if p.passed)
        total_p        = len(student_probes)
        pass_rate      = f"{round(passed/total_p*100)}%" if total_p > 0 else "N/A"

        writer.writerow([
            log.user.student_id or "N/A",
            log.user.full_name,
            log.user.email,
            log.check_in_time.strftime("%Y-%m-%d %H:%M") if log.check_in_time else "",
            log.check_out_time.strftime("%Y-%m-%d %H:%M") if log.check_out_time else "",
            duration,
            log.status,
            total_p,
            passed,
            pass_rate,
        ])

    output.seek(0)

    filename = f"attendance_{session.class_name.replace(' ', '_')}_{session_id}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )