import random
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session as DBSession

from app.database import SessionLocal
from app.models.session import Session as ClassSession
from app.models.attendance_log import AttendanceLog
from app.models.probe_result import ProbeResult
from app.models.anomaly_log import AnomalyLog

PROBE_ACTIONS  = ["blink", "smile", "turn_left", "turn_right"]
PROBE_INTERVAL = 2    # minutes between probe cycles
PROBE_TIMEOUT  = 2    # minutes student has to respond

scheduler = BackgroundScheduler()


def issue_probes():
    """
    Runs on schedule. For every active session,
    randomly picks checked-in students and issues a probe.
    """
    db: DBSession = SessionLocal()
    try:
        # Find all active sessions
        active_sessions = db.query(ClassSession).filter(
            ClassSession.status == "active"
        ).all()

        for session in active_sessions:
            # Get all checked-in students for this session
            logs = db.query(AttendanceLog).filter(
                AttendanceLog.session_id == session.id
            ).all()

            if not logs:
                continue

            # Randomly select 50% of students (minimum 1)
            sample_size = max(1, len(logs) // 2)
            selected    = random.sample(logs, min(sample_size, len(logs)))

            for log in selected:
                # Skip if student already has a pending probe
                existing = db.query(ProbeResult).filter(
                    ProbeResult.user_id    == log.user_id,
                    ProbeResult.session_id == session.id,
                    ProbeResult.status     == "pending"
                ).first()
                if existing:
                    continue

                # Issue new probe with random action
                action = random.choice(PROBE_ACTIONS)
                probe  = ProbeResult(
                    user_id    = log.user_id,
                    session_id = session.id,
                    probe_type = action,
                    status     = "pending",
                )
                db.add(probe)
                print(f"[PROBE] Issued '{action}' probe to user_id={log.user_id} in session {session.id}")

        db.commit()

    except Exception as e:
        print(f"[PROBE ERROR] {e}")
    finally:
        db.close()


def expire_probes():
    """
    Runs on schedule. Marks unanswered probes as expired
    and logs them as anomalies.
    """
    db: DBSession = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=PROBE_TIMEOUT)

        expired_probes = db.query(ProbeResult).filter(
            ProbeResult.status    == "pending",
            ProbeResult.sent_time <= cutoff
        ).all()

        for probe in expired_probes:
            probe.status = "expired"

            # Log as anomaly
            anomaly = AnomalyLog(
                user_id    = probe.user_id,
                session_id = probe.session_id,
                reason     = f"Probe '{probe.probe_type}' expired — no response within {PROBE_TIMEOUT} minutes.",
            )
            db.add(anomaly)
            print(f"[ANOMALY] User {probe.user_id} failed to respond to probe in session {probe.session_id}")

        db.commit()

    except Exception as e:
        print(f"[EXPIRE ERROR] {e}")
    finally:
        db.close()


def start_scheduler():
    """Start background scheduler jobs."""
    scheduler.add_job(issue_probes,  "interval", minutes=PROBE_INTERVAL, id="issue_probes")
    scheduler.add_job(expire_probes, "interval", minutes=1,              id="expire_probes")
    scheduler.start()
    print("[SCHEDULER] Probe engine started ✅")


def stop_scheduler():
    """Stop the scheduler cleanly."""
    scheduler.shutdown()
    print("[SCHEDULER] Probe engine stopped.")