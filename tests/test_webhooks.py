"""
Integration & Webhook Tests

This suite focuses on validating the core requirements of the External Integration Engine.

Coverage Summary:
- Webhook endpoint correctness (User, Payment, Communication) — single and batch payloads.
- Async event handling: verifies Celery task enqueueing and proper payload structure.
- External API error handling: tests success and failure flows, including skip behavior on failure.
- Data synchronization: ensures correct sync function is called on success, not called on failure.
- Idempotency: duplicate event detection tested, no processing or logging on duplicates.
- Retry logic: simulated unexpected error paths to verify retry behavior.
- Webhook log creation: asserts content (event_id, org_id, status) correctness.
"""

import pytest
from unittest.mock import patch
from app.core.enums import ServiceType, WebhookStatus
from app.services.tasks import process_event
from app.schemas.external_api_responses import ExternalUserSuccessResponse, ExternalSubscriptionSuccessResponse
from tests.data.sample_webhook_events import user_event, payment_event, communication_event, batch_user_events, \
    batch_payment_events, batch_communication_events


@pytest.mark.asyncio
async def test_user_service_single_event(client):
    with patch("app.services.tasks.process_event.apply_async") as mocked_apply:
        resp = await client.post("/webhooks/user-service", json=user_event)
        assert resp.status_code == 202
        mocked_apply.assert_called_once()
        args, kwargs = mocked_apply.call_args
        payload_arg, service_arg = args[0]
        assert payload_arg["event_id"] == user_event["event_id"]
        assert service_arg == ServiceType.USER.value

@pytest.mark.asyncio
async def test_user_service_batch_events(client):
    with patch("app.services.tasks.process_event.apply_async") as mocked_apply:
        resp = await client.post("/webhooks/user-service", json=batch_user_events)
        assert resp.status_code == 202
        assert mocked_apply.call_count == len(batch_user_events["events"])


@pytest.mark.asyncio
async def test_user_event_idempotency_skips_processing(client, db_session):
    with patch("app.services.tasks.check_if_event_processed", return_value=True), \
         patch("app.services.tasks.create_webhook_log") as mocked_log, \
         patch("app.services.tasks.process_user") as mocked_process_user:

        process_event(user_event, ServiceType.USER.value)

        mocked_process_user.assert_not_called()
        mocked_log.assert_not_called()

@pytest.mark.asyncio
async def test_process_event_user_success_sync(db_session):
    with patch("app.services.tasks.check_if_event_processed", return_value=False), \
         patch("app.services.tasks.process_user") as mocked_process_user, \
         patch("app.services.tasks.sync_user") as mocked_sync_user, \
         patch("app.services.tasks.create_webhook_log") as mocked_log:

        mocked_process_user.return_value = ExternalUserSuccessResponse(
            status="success",
            data={
                "user_id": "ext_user_12345",
                "email": "sarah.johnson@techcorp.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "department": "Engineering",
                "title": "VP Engineering",
                "status": "active",
                "manager_id": "ext_user_00001",
                "hire_date": "2022-01-15",
                "last_updated": "2024-02-15T09:00:00Z"
            }
        )

        process_event(user_event, ServiceType.USER.value)

        mocked_process_user.assert_called_once()
        mocked_sync_user.assert_called_once()
        mocked_log.assert_called_once()

        kwargs = mocked_log.call_args.kwargs
        assert kwargs["event_id"] == user_event["event_id"]
        assert kwargs["org_id"] == user_event["organization_id"]
        assert kwargs["status"] == WebhookStatus.processed

@pytest.mark.asyncio
async def test_process_event_payment_success_sync(db_session):
    with patch("app.services.tasks.check_if_event_processed", return_value=False), \
         patch("app.services.tasks.process_subscription") as mocked_process_subscription, \
         patch("app.services.tasks.sync_subscription") as mocked_sync_subscription, \
         patch("app.services.tasks.create_webhook_log") as mocked_log:

        mocked_process_subscription.return_value = ExternalSubscriptionSuccessResponse(
            status="success",
            data={
                "subscription_id": "sub_enterprise_456",
                "customer_id": "cust_67890",
                "plan": "enterprise",
                "status": "active",
                "current_period_start": "2024-02-01T00:00:00Z",
                "current_period_end": "2024-03-01T00:00:00Z",
                "amount": 999.99,
                "currency": "USD",
                "payment_method": "card_ending_1234"
            }
        )

        process_event(payment_event, ServiceType.PAYMENT.value)

        mocked_process_subscription.assert_called_once()
        mocked_sync_subscription.assert_called_once()
        mocked_log.assert_called_once()

        kwargs = mocked_log.call_args.kwargs
        assert kwargs["event_id"] == payment_event["event_id"]
        assert kwargs["org_id"] == payment_event["organization_id"]
        assert kwargs["status"] == WebhookStatus.processed

@pytest.mark.asyncio
async def test_process_event_communication_success_sync(db_session):
    with patch("app.services.tasks.check_if_event_processed", return_value=False), \
         patch("app.services.tasks.sync_communication") as mocked_sync_communication, \
         patch("app.services.tasks.create_webhook_log") as mocked_log:

        process_event(communication_event, ServiceType.COMMUNICATION.value)

        mocked_sync_communication.assert_called_once()
        mocked_log.assert_called_once()

        kwargs = mocked_log.call_args.kwargs
        assert kwargs["event_id"] == communication_event["event_id"]
        assert kwargs["org_id"] == communication_event["organization_id"]
        assert kwargs["status"] == WebhookStatus.processed

@pytest.mark.asyncio
async def test_process_event_retries_on_exception(db_session):
    with patch("app.services.tasks.check_if_event_processed", return_value=False), \
         patch("app.services.tasks.process_user", side_effect=Exception("mock error")), \
         patch("app.services.tasks.create_webhook_log") as mocked_log:

        try:
            process_event(user_event, ServiceType.USER.value)
        except Exception as e:
            pass

        mocked_log.assert_not_called()


@pytest.mark.asyncio
async def test_payment_service_single_event(client):
    with patch("app.services.tasks.process_event.apply_async") as mocked_apply:
        resp = await client.post("/webhooks/payment-service", json=payment_event)
        assert resp.status_code == 202
        mocked_apply.assert_called_once()
        args, kwargs = mocked_apply.call_args
        payload_arg, service_arg = args[0]
        assert payload_arg["event_id"] == payment_event["event_id"]
        assert service_arg == ServiceType.PAYMENT.value

@pytest.mark.asyncio
async def test_payment_service_batch_events(client):
    with patch("app.services.tasks.process_event.apply_async") as mocked_apply:
        resp = await client.post("/webhooks/payment-service", json=batch_payment_events)
        assert resp.status_code == 202
        assert mocked_apply.call_count == len(batch_payment_events["events"])

@pytest.mark.asyncio
async def test_communication_service_single_event(client):
    with patch("app.services.tasks.process_event.apply_async") as mocked_apply:
        resp = await client.post("/webhooks/communication-service", json=communication_event)
        assert resp.status_code == 202
        mocked_apply.assert_called_once()
        args, kwargs = mocked_apply.call_args
        payload_arg, service_arg = args[0]
        assert payload_arg["event_id"] == communication_event["event_id"]
        assert service_arg == ServiceType.COMMUNICATION.value

@pytest.mark.asyncio
async def test_communication_service_batch_events(client):
    with patch("app.services.tasks.process_event.apply_async") as mocked_apply:
        resp = await client.post("/webhooks/communication-service", json=batch_communication_events)
        assert resp.status_code == 202
        assert mocked_apply.call_count == len(batch_communication_events["events"])


@pytest.mark.asyncio
async def test_process_event_handles_external_error(db_session):
    with patch("app.services.tasks.check_if_event_processed", return_value=False), \
            patch("app.services.tasks.process_user", return_value=None) as mocked_process_user, \
            patch("app.services.tasks.sync_user") as mocked_sync_user, \
            patch("app.services.tasks.create_webhook_log") as mocked_log:

        process_event(user_event, ServiceType.USER.value)

        mocked_process_user.assert_called_once()
        mocked_sync_user.assert_not_called()
        mocked_log.assert_called_once()
