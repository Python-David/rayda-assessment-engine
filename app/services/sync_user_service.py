from sqlalchemy.orm import Session

from app.core.enums import AuditAction, UserEventType, UserStatus
from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.user import User
from app.schemas.external_api_responses import (
    ExternalUserData,
    ExternalUserSuccessResponse,
)
from app.schemas.webhooks import UserData, UserServiceEvent
from app.utils.audit import log_audit
from app.utils.logger import get_logger

logger = get_logger()


def sync_user(event: UserServiceEvent, external_response: ExternalUserSuccessResponse):
    db: Session = SessionLocal()

    external_id = event.data.user_id
    org_id = event.organization_id
    event_type_str = event.event_type

    try:
        # Validate event type
        if event_type_str not in UserEventType._value2member_map_:
            logger.warning(
                f"Invalid event type '{event_type_str}' for user {external_id}. Skipping."
            )
            return

        event_type = UserEventType(event_type_str)

        org = db.query(Organization).filter(Organization.slug == org_id).first()
        if not org:
            logger.warning(
                f"Organization {org_id} not found for user {external_id}. Skipping sync."
            )
            return

        user = db.query(User).filter(User.external_id == external_id).first()
        external_data = external_response.data

        if event_type == UserEventType.created:
            if user:
                logger.info(f"User {external_id} already exists. Updating.")
                update_user_fields(user, external_data)
                db.commit()
                db.refresh(user)
                log_audit(db, AuditAction.UPDATED_USER, user.id, org.id)
            else:
                logger.info(f"Creating new user {external_id}.")
                user = User(
                    external_id=external_id,
                    email=external_data.email,
                    first_name=external_data.first_name,
                    last_name=external_data.last_name,
                    org_id=org.id,
                    hashed_password=None,
                    status=UserStatus.pending,
                    department=external_data.department,
                    title=external_data.title,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                log_audit(db, AuditAction.CREATED_USER, user.id, org.id)

        elif event_type == UserEventType.updated:
            if not user:
                logger.warning(
                    f"User {external_id} not found on update event. Skipping."
                )
                return
            logger.info(f"Updating existing user {external_id}.")
            update_user_fields(user, external_data)
            db.commit()
            db.refresh(user)
            log_audit(db, AuditAction.UPDATED_USER, user.id, org.id)

        elif event_type == UserEventType.deleted:
            if not user:
                logger.warning(
                    f"User {external_id} not found on delete event. Skipping."
                )
                return
            logger.info(f"Deactivating user {external_id}.")
            user.status = UserStatus.inactive
            db.commit()
            db.refresh(user)
            log_audit(db, AuditAction.DELETED_USER, user.id, org.id)

        else:
            logger.warning(
                f"Unhandled event type '{event_type}' for user {external_id}. Skipping."
            )

    except Exception as e:
        logger.exception(f"Error syncing user {external_id}: {e}")
        db.rollback()
    finally:
        db.close()


def update_user_fields(user: User, data: ExternalUserData):
    user.email = data.email or user.email
    user.first_name = data.first_name or user.first_name
    user.last_name = data.last_name or user.last_name
    user.department = data.department or user.department
    user.title = data.title or user.title
    user.status = data.status or user.status
