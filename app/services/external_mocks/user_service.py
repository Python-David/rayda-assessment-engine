from datetime import datetime

from app.core.enums import ServiceType
from app.schemas.external_api_responses import (
    ExternalUserErrorResponse,
    ExternalUserListSuccessResponse,
    ExternalUserSuccessResponse,
)
from app.schemas.webhooks import UserData
from app.services.external_mocks import mock_responses
from app.services.external_mocks.shared import simulate_failure
from app.utils.logger import get_logger

logger = get_logger()


def process_user(
    data: UserData,
) -> ExternalUserSuccessResponse | ExternalUserErrorResponse:
    """
    Simulated external User Management Service.

    This function represents an outbound call to a hypothetical external user management system.
    It uses `simulate_failure()` to simulate transport-level failures (e.g., service downtime).

    Additionally, it uses a hardcoded "magic" user_id value ('ext_user_99999') to deterministically simulate
    a business-level error response (e.g., "User not found"). This pattern is commonly used in integration testing
    and sandbox environments (similar to Stripe test cards or Twilio test numbers).

    Returns a Pydantic success response or error response based on conditions, allowing us to test
    error handling and local sync logic.
    """
    logger.info(f"Calling User Management Service with data: {data}")

    simulate_failure(ServiceType.USER)

    # Example error simulation based on user_id from our data seed (simulate from frontend)
    if data.user_id == "ext_user_99999":
        error_response = mock_responses.user_error_response.copy()
        error_response.timestamp = datetime.now()
        return error_response

    success_response = mock_responses.user_success_response.copy()
    success_response.data.user_id = data.user_id
    success_response.data.email = data.email
    success_response.data.first_name = data.first_name
    success_response.data.last_name = data.last_name
    success_response.data.department = data.department
    success_response.data.title = data.title
    success_response.data.last_updated = datetime.now()

    return success_response


def list_users() -> ExternalUserListSuccessResponse:
    """
    Simulated external User Management Service list_users endpoint.

    Returns a mocked paginated user list response.
    """
    logger.info("Calling User Management Service list_users endpoint.")

    simulate_failure(ServiceType.USER)

    return mock_responses.user_list_success_response
