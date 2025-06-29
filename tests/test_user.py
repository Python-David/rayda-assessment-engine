import pytest

from app.core.config import settings


@pytest.mark.asyncio
async def test_admin_can_create_user(client, initial_admin_user):
    login_resp = await client.post("/users/login", data={"username": settings.INITIAL_ADMIN_EMAIL, "password": settings.INITIAL_ADMIN_PASSWORD})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    user_payload = {
        "email": "user1@testorg.com",
        "password": "UserPass123!",
        "role": "user"
    }
    resp = await client.post("/users/", json=user_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "user1@testorg.com"

@pytest.mark.asyncio
async def test_user_cannot_create_user(client):
    # Login as basic user
    # First create
    login_admin = await client.post("/users/login", data={"username": settings.INITIAL_ADMIN_EMAIL, "password": settings.INITIAL_ADMIN_PASSWORD})
    admin_token = login_admin.json()["access_token"]

    create_user_payload = {
        "email": "basicuser@testorg.com",
        "password": "BasicPass123!",
        "role": "user"
    }
    await client.post("/users/", json=create_user_payload, headers={"Authorization": f"Bearer {admin_token}"})

    # Login as basic user
    login_user = await client.post("/users/login", data={"username": "basicuser@testorg.com", "password": "BasicPass123!"})
    user_token = login_user.json()["access_token"]

    # Try to create another user
    new_user_payload = {
        "email": "shouldfail@testorg.com",
        "password": "FailPass123!",
        "role": "user"
    }
    resp = await client.post("/users/", json=new_user_payload, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403
