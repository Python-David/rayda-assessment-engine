"""
Integration Status Endpoint Tests

This suite focuses on validating the core requirements of the integration monitoring layer via the /integrations/status endpoint.

Coverage Summary:
- Access control: verifies that only admins and superadmins can access integration status.
- Health computation: validates "error" state when no success logs exist.
- Health computation: validates "healthy" state when last success is most recent.
- Health computation: validates "degraded" state when a newer failure exists after the last success.
- Correct per-service breakdown: confirms that each service (user, payment, communication) is represented and handled individually.

Highlights:
- Uses DB setup and controlled log insertion to simulate real webhook processing scenarios.
- Confirms correct status logic in different sequences of success and failure events.
- Ensures accurate and secure visibility of integration health to authorized users only.
- Complements webhook and sync service tests by verifying observability and monitoring requirements.

These tests collectively validate the robustness and correctness of the integration health reporting mechanism.
"""
import pytest

from app.core.config import settings
from app.models.webhooks import WebhookLog
from app.core.enums import ServiceType, WebhookStatus

@pytest.mark.asyncio
async def test_admin_can_fetch_status(client, db_session, superadmin_user, test_org):
    login_resp = await client.post("/users/login", data={
        "username": settings.INITIAL_SUPERADMIN_EMAIL,
        "password": settings.INITIAL_SUPERADMIN_PASSWORD
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    resp = await client.get("/integrations/status", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    json_data = resp.json()
    assert "user_service" in json_data
    assert "payment_service" in json_data
    assert "communication_service" in json_data

@pytest.mark.asyncio
async def test_non_admin_forbidden(client, db_session, test_user):
    login_resp = await client.post("/users/login", data={
        "username": test_user.email,
        "password": "test_user_password"
    })
    token = login_resp.json()["access_token"]

    resp = await client.get("/integrations/status", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_status_shows_error_when_no_success_logs(client, db_session, superadmin_user, test_org):
    login_resp = await client.post("/users/login", data={
        "username": settings.INITIAL_SUPERADMIN_EMAIL,
        "password": settings.INITIAL_SUPERADMIN_PASSWORD
    })
    token = login_resp.json()["access_token"]

    db_session.query(WebhookLog).delete()
    db_session.commit()

    resp = await client.get("/integrations/status", headers={"Authorization": f"Bearer {token}"})
    data = resp.json()

    assert data["user_service"]["status"] == "error"
    assert data["payment_service"]["status"] == "error"
    assert data["communication_service"]["status"] == "error"

@pytest.mark.asyncio
async def test_status_healthy_when_success_and_no_failures(client, db_session, superadmin_user, test_org):
    db_session.query(WebhookLog).delete()
    db_session.commit()

    success_log = WebhookLog(
        event_id="evt_user_success",
        service=ServiceType.USER,
        org_id="org_001",
        status=WebhookStatus.processed,
        payload={}
    )
    db_session.add(success_log)
    db_session.commit()

    login_resp = await client.post("/users/login", data={
        "username": settings.INITIAL_SUPERADMIN_EMAIL,
        "password": settings.INITIAL_SUPERADMIN_PASSWORD
    })
    token = login_resp.json()["access_token"]

    resp = await client.get("/integrations/status", headers={"Authorization": f"Bearer {token}"})
    data = resp.json()

    assert data["user_service"]["status"] == "healthy"

@pytest.mark.asyncio
async def test_status_degraded_when_failure_after_success(client, db_session, superadmin_user, test_org):
    db_session.query(WebhookLog).delete()
    db_session.commit()

    success_log = WebhookLog(
        event_id="evt_user_success",
        service=ServiceType.USER,
        org_id="org_001",
        status=WebhookStatus.processed,
        payload={}
    )
    db_session.add(success_log)
    db_session.commit()

    failure_log = WebhookLog(
        event_id="evt_user_fail",
        service=ServiceType.USER,
        org_id="org_001",
        status=WebhookStatus.failed,
        payload={}
    )
    db_session.add(failure_log)
    db_session.commit()

    login_resp = await client.post("/users/login", data={
        "username": settings.INITIAL_SUPERADMIN_EMAIL,
        "password": settings.INITIAL_SUPERADMIN_PASSWORD
    })
    token = login_resp.json()["access_token"]

    resp = await client.get("/integrations/status", headers={"Authorization": f"Bearer {token}"})
    data = resp.json()

    assert data["user_service"]["status"] == "degraded"
