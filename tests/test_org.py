import pytest

@pytest.mark.asyncio
async def test_superadmin_can_create_org(client):
    # Login superadmin
    login_resp = await client.post("/users/login", data={"username": "superadmin@example.com", "password": "SuperSecret123!"})
    token = login_resp.json()["access_token"]

    # Create org
    org_payload = {
        "name": "TestOrg",
        "slug": "testorg",
        "initial_admin_email": "admin@testorg.com",
        "initial_admin_password": "AdminPass123!"
    }
    resp = await client.post("/orgs/", json=org_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "TestOrg"

@pytest.mark.asyncio
async def test_admin_cannot_create_org(client):
    # Login as initial admin
    login_resp = await client.post("/users/login", data={"username": "admin@testorg.com", "password": "AdminPass123!"})
    token = login_resp.json()["access_token"]

    org_payload = {
        "name": "AnotherOrg",
        "slug": "anotherorg",
        "initial_admin_email": "another_admin@test.com",
        "initial_admin_password": "AdminPass123!"
    }
    resp = await client.post("/orgs/", json=org_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
