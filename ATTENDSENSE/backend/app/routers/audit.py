from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.anomaly_log import AnomalyLog
from app.utils.jwt import decode_token

router      = APIRouter(prefix="/audit", tags=["Audit & Anomaly Logs"])
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


@router.get("/logs")
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get recent audit logs."""
    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).limit(limit).all()

    return [
        {
            "id"       : log.id,
            "actor"    : log.actor.full_name if log.actor else "System",
            "action"   : log.action,
            "detail"   : log.detail,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@router.get("/anomalies")
def get_all_anomalies(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get all anomalies across all sessions."""
    anomalies = db.query(AnomalyLog).order_by(
        AnomalyLog.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id"        : a.id,
            "student"   : a.user.full_name,
            "session"   : a.session.class_name,
            "reason"    : a.reason,
            "flagged_at": a.created_at,
        }
        for a in anomalies
    ]


@router.post("/log-action")
def manual_audit_log(
    action: str,
    detail: str = None,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Manually write an audit log entry."""
    entry = AuditLog(
        actor_id = current_user.id,
        action   = action,
        detail   = detail,
    )
    db.add(entry)
    db.commit()
    return {"message": "Audit log recorded ✅"}