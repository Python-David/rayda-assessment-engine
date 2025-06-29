from app.core.config import settings
from app.schemas.external_api_responses import ExternalUserSuccessResponse, ExternalSubscriptionSuccessResponse
from app.schemas.webhooks import UserServiceEvent, BaseWebhookEvent, PaymentServiceEvent, CommunicationServiceEvent
from app.services.external_mocks import payment_service, communication_service
from app.services.external_mocks.payment_service import process_subscription
from app.services.external_mocks.user_service import process_user
from app.services.sync_communication import sync_communication
from app.services.sync_payment_service import sync_subscription
from app.services.sync_user_service import sync_user
from app.worker import celery_app
from app.utils.logger import get_logger
from app.core.enums import ServiceType

logger = get_logger()

@celery_app.task(bind=True, max_retries=settings.CELERY_MAX_RETRIES)
def process_event(self, event: dict, service_name: str):
    try:
        parsed_event = BaseWebhookEvent(**event)
        logger.info(f"Processing event: {parsed_event.event_id} for {service_name}")

        service_enum = ServiceType(service_name)

        if service_enum == ServiceType.USER:
            parsed_user_event = UserServiceEvent(**event)
            response = process_user(parsed_user_event.data)
            if isinstance(response, ExternalUserSuccessResponse):
                sync_user(parsed_user_event, response)
            else:
                logger.warning(
                    f"External user service returned error for user {parsed_user_event.data.user_id}. Skipping local sync.")
        elif service_enum == ServiceType.PAYMENT:
            parsed_payment_event = PaymentServiceEvent(**event)
            response = process_subscription(parsed_payment_event.data)
            if isinstance(response, ExternalSubscriptionSuccessResponse):
                sync_subscription(parsed_payment_event, response)
            else:
                logger.warning(
                    f"External payment service returned error for subscription {getattr(parsed_payment_event.data, 'subscription_id', 'unknown')}. Skipping local sync."
                )
        elif service_enum == ServiceType.COMMUNICATION:
            parsed_comm_event = CommunicationServiceEvent(**event)
            sync_communication(parsed_comm_event)
        else:
            logger.warning(f"Unknown service: {service_name}")

        logger.info(f"Event processed successfully: {parsed_event.event_id} for {service_name}")

    except Exception as exc:
        try:
            countdown = settings.CELERY_RETRY_BACKOFF_BASE ** self.request.retries
            logger.warning(f"Retry #{self.request.retries + 1} for event {event.get('event_id', 'unknown')} in {countdown} seconds")
            raise self.retry(exc=exc, countdown=countdown)
        except self.MaxRetriesExceededError:
            logger.error(f"Permanent failure: {event.get('event_id', 'unknown')}")
            # Log to IntegrationFailureLog or DB
            pass
