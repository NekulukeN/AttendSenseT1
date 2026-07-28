from app.models.audit_log import AuditLog
from sqlalchemy.orm import Session as DBSession

def log_action(db: DBSession, actor_id: int, action: str, detail: str = None):
    """Helper to write an audit log entry anywhere in the app."""
    entry = AuditLog(
        actor_id = actor_id,
        action   = action,
        detail   = detail,
    )
    db.add(entry)
    db.commit()