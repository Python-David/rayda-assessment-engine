from datetime import datetime

from sqlalchemy.orm import Session
from app.core.enums import WebhookStatus, ServiceType
from app.models.webhooks import WebhookLog


def serialize_for_json(obj):
    """
    Recursively converts any datetime objects to ISO strings so dicts can be safely JSON-encoded.
    """
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(i) for i in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

def check_if_event_processed(db: Session, event_id: str) -> bool:
    """
    Check if an event with the given event_id has already been processed.
    """
    existing_log = db.query(WebhookLog).filter_by(event_id=event_id).first()
    return existing_log is not None

def create_webhook_log(
    db: Session,
    event_id: str,
    service: ServiceType,
    org_id: str,
    status: WebhookStatus,
    payload: dict
):
    """
    Create a log entry for a webhook event.
    """
    serialized_payload = serialize_for_json(payload)

    log_entry = WebhookLog(
        event_id=event_id,
        service=service,
        org_id=org_id,
        status=status,
        payload=serialized_payload
    )
    db.add(log_entry)
    db.commit()
