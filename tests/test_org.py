import pytest

from app.core.config import settings
from app.core.enums import AuditAction
from app.models.audit_log import AuditLog
from app.models.organization import Organization


@pytest.mark.asyncio
async def test_superadmin_can_create_org(client, superadmin_user):
    login_resp = await client.post(
        "/users/login",
        data={
            "username": settings.INITIAL_SUPERADMIN_EMAIL,
            "password": settings.INITIAL_SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    org_payload = {
        "name": "TestOrg",
        "slug": "testorg",
        "initial_admin_email": settings.INITIAL_ADMIN_EMAIL,
        "initial_admin_password": settings.INITIAL_ADMIN_PASSWORD,
    }
    resp = await client.post(
        "/orgs/", json=org_payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "TestOrg"


@pytest.mark.asyncio
async def test_admin_cannot_create_org(client, initial_admin_user):
    # Login as initial admin
    login_resp = await client.post(
        "/users/login",
        data={
            "username": settings.INITIAL_ADMIN_EMAIL,
            "password": settings.INITIAL_ADMIN_PASSWORD,
        },
    )
    token = login_resp.json()["access_token"]

    org_payload = {
        "name": "AnotherOrg",
        "slug": "anotherorg",
        "initial_admin_email": "another_admin@test.com",
        "initial_admin_password": "AdminPass123!",
    }
    resp = await client.post(
        "/orgs/", json=org_payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_superadmin_create_org_creates_two_audit_logs(
    client, db_session, superadmin_user
):
    login_resp = await client.post(
        "/users/login",
        data={
            "username": settings.INITIAL_SUPERADMIN_EMAIL,
            "password": settings.INITIAL_SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    org_payload = {
        "name": "AuditLogOrg",
        "slug": "auditlogorg",
        "initial_admin_email": "newadmin@auditlogorg.com",
        "initial_admin_password": "AdminPass123!",
    }
    resp = await client.post(
        "/orgs/", json=org_payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "AuditLogOrg"

    new_org_slug = org_payload["slug"]
    new_org = db_session.query(Organization).filter_by(slug=new_org_slug).first()
    assert new_org is not None

    audit_logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.org_id == new_org.id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    assert len(audit_logs) >= 2

    org_log = next(
        (log for log in audit_logs if log.action == AuditAction.CREATED_ORG), None
    )
    assert org_log is not None
    assert org_log.user_id == superadmin_user.id
    assert org_log.org_id == new_org.id

    user_log = next(
        (log for log in audit_logs if log.action == AuditAction.CREATED_USER), None
    )
    assert user_log is not None
    assert user_log.user_id == superadmin_user.id
    assert user_log.org_id == new_org.id
