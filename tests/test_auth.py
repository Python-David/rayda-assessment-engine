import pytest

@pytest.mark.asyncio
async def test_superadmin_login(client):
    resp = await client.post("/users/login", data={"username": "superadmin@example.com", "password": "SuperSecret123!"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
