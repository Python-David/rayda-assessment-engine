from datetime import datetime

from app.schemas.external_api_responses import ExternalSubscriptionSuccessResponse
from app.schemas.webhooks import SubscriptionCreatedData, PaymentFailedData
from app.services.external_mocks import mock_responses
from app.services.external_mocks.shared import simulate_failure
from app.utils.logger import get_logger
from app.core.enums import ServiceType

logger = get_logger()

def process_subscription(data: SubscriptionCreatedData | PaymentFailedData) -> ExternalSubscriptionSuccessResponse:
    """
    Simulated external Payment Service.

    This function represents an outbound call to a billing/billing system.
    It uses `simulate_failure()` to simulate transport-level failures (e.g., external API unavailable).

    Additionally, it uses a hardcoded "magic" subscription_id value ('sub_invalid_999') to deterministically simulate
    a business-level error response (e.g., "Subscription not found"). This mirrors real-world practices where
    sandbox or test environments allow triggering controlled errors using specific values.

    Returns a Pydantic success response or error response depending on the conditions, supporting robust
    retry logic and error handling workflows.
    """
    logger.info(f"Calling Payment Service with data: {data}")

    simulate_failure(ServiceType.PAYMENT)

    # Example error simulation based on user_id from our data seed (simulate from frontend)
    if data.subscription_id == "sub_invalid_999":
        error_response = mock_responses.subscription_error_response.copy()
        error_response.timestamp = datetime.now()
        return error_response

    success_response = mock_responses.subscription_success_response.copy()
    success_response.data.subscription_id = getattr(data, "subscription_id", success_response.data.subscription_id)
    success_response.data.customer_id = getattr(data, "customer_id", success_response.data.customer_id)
    success_response.data.plan = getattr(data, "plan", success_response.data.plan)
    success_response.data.status = getattr(data, "status", success_response.data.status)
    success_response.data.amount = getattr(data, "amount", success_response.data.amount)
    success_response.data.currency = getattr(data, "currency", success_response.data.currency)
    success_response.data.payment_method = success_response.data.payment_method

    return success_response