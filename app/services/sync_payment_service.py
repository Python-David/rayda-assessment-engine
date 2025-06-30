from sqlalchemy.orm import Session

from app.core.enums import AuditAction, SubscriptionEventType, SubscriptionStatus
from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.external_api_responses import (
    ExternalSubscriptionData,
    ExternalSubscriptionSuccessResponse,
)
from app.schemas.webhooks import PaymentServiceEvent
from app.utils.audit import log_audit
from app.utils.logger import get_logger

logger = get_logger()


def sync_subscription(
    event: PaymentServiceEvent, external_response: ExternalSubscriptionSuccessResponse
):
    db: Session = SessionLocal()

    external_data = external_response.data
    sub_id = external_data.subscription_id

    try:
        org_id_str = event.organization_id
        event_type_str = event.event_type

        # Validate event type
        if event_type_str not in SubscriptionEventType._value2member_map_:
            logger.warning(
                f"Invalid event type '{event_type_str}' for subscription {sub_id}. Skipping."
            )
            return

        event_type = SubscriptionEventType(event_type_str)

        # Validate organization
        org = db.query(Organization).filter(Organization.slug == org_id_str).first()
        if not org:
            logger.warning(
                f"Organization {org_id_str} not found. Skipping subscription sync."
            )
            return

        # Validate user by external_id = customer_id from external data
        user = (
            db.query(User).filter(User.external_id == external_data.customer_id).first()
        )
        if not user:
            logger.warning(
                f"User with external_id (customer_id) {external_data.customer_id} not found. Skipping subscription sync."
            )
            return

        subscription = (
            db.query(Subscription)
            .filter(Subscription.external_subscription_id == sub_id)
            .first()
        )

        if event_type == SubscriptionEventType.created:
            if subscription:
                logger.info(f"Subscription {sub_id} already exists. Updating.")
                update_subscription_fields(subscription, external_data)
                db.commit()
                db.refresh(subscription)
                log_audit(db, AuditAction.UPDATED_SUBSCRIPTION, user.id, org.id)
            else:
                logger.info(f"Creating new subscription {sub_id}.")
                subscription = Subscription(
                    external_subscription_id=sub_id,
                    user_id=user.id,
                    plan=external_data.plan,
                    status=external_data.status,
                    billing_cycle=event.data.billing_cycle,
                    amount=external_data.amount,
                    currency=external_data.currency,
                    trial_end=event.data.trial_end,
                )
                db.add(subscription)
                db.commit()
                db.refresh(subscription)
                log_audit(db, AuditAction.CREATED_SUBSCRIPTION, user.id, org.id)

        elif event_type == SubscriptionEventType.failed:
            if not subscription:
                logger.warning(
                    f"Subscription {sub_id} not found on payment failure event. Skipping."
                )
                return

            logger.info(f"Processing payment failure for subscription {sub_id}.")
            subscription.status = SubscriptionStatus.failed
            db.commit()
            db.refresh(subscription)
            log_audit(db, AuditAction.PAYMENT_FAILED_SUBSCRIPTION, user.id, org.id)

        else:
            logger.warning(
                f"Unhandled event type '{event_type}' in payment event. Skipping."
            )

    except Exception as e:
        logger.exception(f"Error syncing subscription {sub_id}: {e}")
        db.rollback()
    finally:
        db.close()


def update_subscription_fields(
    subscription: Subscription, data: ExternalSubscriptionData
):
    subscription.plan = data.plan or subscription.plan
    subscription.status = data.status or subscription.status
    subscription.amount = data.amount or subscription.amount
    subscription.currency = data.currency or subscription.currency
    subscription.customer_id = data.customer_id or subscription.customer_id
