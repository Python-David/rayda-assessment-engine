"""
Rate Limiting Tests

This suite focuses on validating the enforcement of request rate limits on webhook endpoints.

Coverage Summary:
- Verifies allowed requests succeed up to the configured rate limit.
- Confirms correct 429 Too Many Requests response is returned when limit is exceeded.
- Ensures rate limiting integrates properly with authentication (JWT-protected routes).
- Uses patching to bypass Celery task execution, focusing purely on request-level rate limit behavior.

Highlights:
- Fully tests the end-to-end rate limiting logic (from request count tracking to blocking).
- Confirms that SlowAPI is configured correctly and active in the FastAPI stack.
- Ensures real-world simulation of repeated requests from the same authenticated client.
"""

from unittest.mock import patch

import pytest
from fastapi import status

from app.core.config import settings
from tests.data.sample_webhook_events import communication_event


@pytest.mark.asyncio
async def test_rate_limit_exceeded(client, superadmin_user, test_org):
    login_resp = await client.post(
        "/users/login",
        data={
            "username": settings.INITIAL_SUPERADMIN_EMAIL,
            "password": settings.INITIAL_SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.services.tasks.process_event.apply_async"):
        for i in range(settings.WEBHOOK_RATE_LIMIT_COUNT):
            resp = await client.post(
                "/webhooks/communication-service",
                json=communication_event,
                headers=headers,
            )
            assert resp.status_code == status.HTTP_202_ACCEPTED

        # One more to exceed
        resp = await client.post(
            "/webhooks/communication-service", json=communication_event, headers=headers
        )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in resp.text
