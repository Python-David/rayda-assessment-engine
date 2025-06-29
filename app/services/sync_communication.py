from sqlalchemy.orm import Session
from app.models.communication_log import CommunicationLog
from app.models.organization import Organization
from app.models.user import User
from app.db.session import SessionLocal
from app.utils.logger import get_logger
from app.schemas.webhooks import CommunicationServiceEvent, MessageDeliveredData, MessageBouncedData

logger = get_logger()

def sync_communication(event: CommunicationServiceEvent):
    db: Session = SessionLocal()

    try:
        org_id_str = event.organization_id
        event_type_str = event.event_type

        # Validate organization
        org = db.query(Organization).filter(Organization.slug == org_id_str).first()
        if not org:
            logger.warning(f"Organization {org_id_str} not found. Skipping communication sync.")
            return

        data = event.data

        # Find user by recipient email
        user = db.query(User).filter(User.email == data.recipient).first()
        if not user:
            logger.warning(f"User with email {data.recipient} not found. Logging without user link.")
            user_id = None
        else:
            user_id = user.id

        comm_log = db.query(CommunicationLog).filter(CommunicationLog.message_id == data.message_id).first()

        if comm_log:
            logger.info(f"Updating communication log for message {data.message_id}.")
            comm_log.status = data.status if hasattr(data, "status") else "bounced"
            comm_log.delivery_time_ms = str(data.delivery_time_ms) if hasattr(data, "delivery_time_ms") else comm_log.delivery_time_ms
            comm_log.template = data.template or comm_log.template
        else:
            logger.info(f"Creating new communication log for message {data.message_id}.")
            comm_log = CommunicationLog(
                message_id=data.message_id,
                user_id=user_id,
                status=data.status if hasattr(data, "status") else "bounced",
                template=data.template,
                delivery_time_ms=str(data.delivery_time_ms) if hasattr(data, "delivery_time_ms") else None,
            )
            db.add(comm_log)

        db.commit()
        db.refresh(comm_log)

    except Exception as e:
        logger.exception(f"Error syncing communication log for message {getattr(data, 'message_id', 'unknown')}: {e}")
        db.rollback()
    finally:
        db.close()
