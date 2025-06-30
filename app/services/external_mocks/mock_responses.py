from datetime import datetime

from app.schemas.external_api_responses import (
    ExternalCustomerUsageData,
    ExternalCustomerUsageMetrics,
    ExternalCustomerUsageSuccessResponse,
    ExternalMessageData,
    ExternalMessageErrorResponse,
    ExternalMessageSuccessResponse,
    ExternalSubscriptionData,
    ExternalSubscriptionErrorResponse,
    ExternalSubscriptionSuccessResponse,
    ExternalUserData,
    ExternalUserErrorResponse,
    ExternalUserListData,
    ExternalUserListSuccessResponse,
    ExternalUserSuccessResponse,
    ExternalUserSummary,
    Pagination,
)

user_success_response = ExternalUserSuccessResponse(
    status="success",
    data=ExternalUserData(
        user_id="ext_user_12345",
        email="sarah.johnson@techcorp.com",
        first_name="Sarah",
        last_name="Johnson",
        department="Engineering",
        title="VP Engineering",
        status="active",
        manager_id="ext_user_00001",
        hire_date="2022-01-15",
        last_updated=datetime.now(),
    ),
)

user_error_response = ExternalUserErrorResponse(
    status="error",
    error_code="USER_NOT_FOUND",
    message="User with ID ext_user_99999 not found",
    timestamp=datetime.now(),
)

user_list_success_response = ExternalUserListSuccessResponse(
    status="success",
    data=ExternalUserListData(
        users=[
            ExternalUserSummary(
                user_id="ext_user_12345",
                email="sarah.johnson@techcorp.com",
                first_name="Sarah",
                last_name="Johnson",
                status="active",
            ),
            ExternalUserSummary(
                user_id="ext_user_54321",
                email="john.doe@techcorp.com",
                first_name="John",
                last_name="Doe",
                status="active",
            ),
        ],
        pagination=Pagination(
            total=150,
            page=1,
            per_page=50,
            has_more=True,
        ),
    ),
)

subscription_success_response = ExternalSubscriptionSuccessResponse(
    status="success",
    data=ExternalSubscriptionData(
        subscription_id="sub_enterprise_456",
        customer_id="cust_67890",
        plan="enterprise",
        status="active",
        current_period_start=datetime(2024, 2, 1, 0, 0, 0),
        current_period_end=datetime(2024, 3, 1, 0, 0, 0),
        amount=999.99,
        currency="USD",
        payment_method="card_ending_1234",
    ),
)

subscription_error_response = ExternalSubscriptionErrorResponse(
    status="error",
    error_code="SUBSCRIPTION_NOT_FOUND",
    message="Subscription with ID sub_invalid_999 not found",
    timestamp=datetime.now(),
)


customer_usage_success_response = ExternalCustomerUsageSuccessResponse(
    status="success",
    data=ExternalCustomerUsageData(
        customer_id="cust_67890",
        billing_period="2024-02",
        usage_metrics=ExternalCustomerUsageMetrics(
            api_calls=45000,
            storage_gb=125.5,
            compute_hours=89.2,
        ),
        overage_charges=150.0,
        total_amount=1149.99,
    ),
)

message_success_response = ExternalMessageSuccessResponse(
    status="success",
    data=ExternalMessageData(
        message_id="msg_abc_123",
        status="delivered",
        delivered_at=datetime.now(),
    ),
)

message_error_response = ExternalMessageErrorResponse(
    status="error",
    error_code="MESSAGE_NOT_FOUND",
    message="Message with ID msg_invalid_999 not found",
    timestamp=datetime.now(),
)
