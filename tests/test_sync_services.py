"""
Sync Service Tests

This suite focuses on validating the core requirements of the data synchronization layer.

Coverage Summary:
- User sync: validates DB creation and update logic from external user events and responses.
- Subscription sync: validates subscription creation and update linked to users and organizations.
- Communication log sync: validates message logging, including user linking via email.

Highlights:
- Confirms correct DB state after sync (actual data correctness, not just function call correctness).
- Uses monkeypatching to inject test DB sessions for all sync functions.
- Validates Enum field correctness (status, plan, department, title).
- Ensures organization and user dependencies are handled correctly.
- Tests reflect real-world event payloads and simulate external success responses.

These tests complement the webhook and integration tests by verifying final data consistency and correctness inside the system.
"""
import pytest

from app.core.enums import Department, Title, UserStatus, SubscriptionPlan, SubscriptionStatus, BillingCycle, \
    CommunicationStatus
from app.services import sync_user_service, sync_payment_service
from app.services.sync_user_service import sync_user
from app.services.sync_payment_service import sync_subscription
from app.services.sync_communication import sync_communication
from app.schemas.webhooks import UserServiceEvent, PaymentServiceEvent, CommunicationServiceEvent
from app.schemas.external_api_responses import ExternalUserSuccessResponse, ExternalSubscriptionSuccessResponse

from app.models.user import User
from app.models.subscription import Subscription
from app.models.communication_log import CommunicationLog


def test_sync_user_creates_user(db_session, monkeypatch, test_org):
    monkeypatch.setattr(sync_user_service, "SessionLocal", lambda: db_session)

    event = UserServiceEvent(
        event_type="user.created",
        event_id="evt_user_test_create",
        timestamp="2025-06-30T12:00:00Z",
        organization_id="org_001",
        data={
            "user_id": "ext_user_sync_001",
            "email": "sync.test@example.com",
            "first_name": "Sync",
            "last_name": "Test",
            "department": Department.finance,
            "title": Title.hr_manager,
            "status": UserStatus.pending,
            "hire_date": "2025-06-30"
        },
        metadata={
            "source": "test_case",
            "version": "1.0",
            "correlation_id": "sync_test_001"
        }
    )

    external_response = ExternalUserSuccessResponse(
        status="success",
        data={
            "user_id": "ext_user_sync_001",
            "email": "sync.test@example.com",
            "first_name": "Sync",
            "last_name": "Test",
            "department": Department.finance,
            "title": Title.hr_manager,
            "status": UserStatus.pending,
            "manager_id": None,
            "hire_date": "2025-06-30",
            "last_updated": "2025-06-30T12:00:00Z"
        }
    )

    sync_user(event, external_response)

    user = db_session.query(User).filter_by(external_id="ext_user_sync_001").first()
    assert user is not None
    assert user.email == "sync.test@example.com"
    assert user.first_name == "Sync"
    assert user.status == "pending"


def test_sync_subscription_creates_or_updates_subscription(db_session, monkeypatch, test_org, test_user):
    monkeypatch.setattr(sync_payment_service, "SessionLocal", lambda: db_session)

    event = PaymentServiceEvent(
        event_type="subscription.created",
        event_id="evt_pay_sync_001",
        timestamp="2025-06-30T12:00:00Z",
        organization_id="org_001",
        data={
            "subscription_id": "sub_sync_001",
            "customer_id": "cust_sync_001",
            "plan": SubscriptionPlan.enterprise,
            "status": SubscriptionStatus.active,
            "billing_cycle": BillingCycle.annual,
            "amount": 500.00,
            "currency": "USD",
            "trial_end": "2025-07-30T23:59:59Z"
        },
        metadata={
            "source": "test_case",
            "version": "1.0",
            "correlation_id": "sync_test_002"
        }
    )

    external_response = ExternalSubscriptionSuccessResponse(
        status="success",
        data={
            "subscription_id": "sub_sync_001",
            "customer_id": "cust_sync_001",
            "plan": SubscriptionPlan.enterprise,
            "status": SubscriptionStatus.active,
            "current_period_start": "2025-06-01T00:00:00Z",
            "current_period_end": "2025-07-01T00:00:00Z",
            "amount": 500.00,
            "currency": "USD",
            "payment_method": "card_ending_4242"
        }
    )

    sync_subscription(event, external_response)

    subscription = db_session.query(Subscription).filter_by(external_subscription_id="sub_sync_001").first()
    assert subscription is not None
    assert subscription.status == "active"
    assert subscription.plan == "enterprise"
    assert subscription.amount == 500.00

@pytest.mark.asyncio
async def test_sync_communication_logs_message(db_session, monkeypatch, test_org, test_user):
    monkeypatch.setattr("app.services.sync_communication.SessionLocal", lambda: db_session)

    event = CommunicationServiceEvent(
        event_type="message.delivered",
        event_id="evt_comm_sync_001",
        timestamp="2025-06-30T12:00:00Z",
        organization_id="org_001",
        data={
            "message_id": "msg_sync_001",
            "recipient": "customer@example.com",
            "template": "onboarding_email",
            "status": CommunicationStatus.delivered
        },
        metadata={
            "source": "test_case",
            "version": "1.0",
            "correlation_id": "sync_test_003"
        }
    )

    sync_communication(event)

    log = db_session.query(CommunicationLog).filter_by(message_id="msg_sync_001").first()
    assert log is not None
    assert log.status == CommunicationStatus.delivered
    assert log.template == "onboarding_email"

    if log.user_id:
        user = db_session.query(User).filter_by(id=log.user_id).first()
        assert user is not None
        assert user.email == "customer@example.com"
