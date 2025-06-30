from app.core.enums import AuditAction
from app.models.audit_log import AuditLog


def log_audit(db, action: AuditAction, user_id: str, org_id: str):
    audit_log = AuditLog(
        action=action,
        user_id=user_id,
        org_id=org_id,
    )
    db.add(audit_log)
    db.commit()
