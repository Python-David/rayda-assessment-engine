from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.webhooks import WebhookLog
from app.models.user import User
from app.core.enums import ServiceType, WebhookStatus, UserRole
from app.core.auth import get_current_active_user
from app.schemas.integrations import ServiceIntegrationStatus, IntegrationStatusResponse

router = APIRouter()

@router.get("/status", response_model=IntegrationStatusResponse)
def integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve the current health status of all external service integrations.

    Only accessible by admins and superadmins.

    This endpoint provides a per-service summary including:
    - Timestamp of the last successfully processed event (`last_success`)
    - ID of the last successful event (`last_event_id`)
    - Overall health status, which can be:
        - 'healthy': Most recent event was successfully processed, no newer failures
        - 'degraded': Last success exists, but there is a more recent failure
        - 'error': No successful events found

    The statuses help administrators quickly determine if any integration is failing
    or requires investigation.

    Returns:
        JSON object with keys as service names and values as status details.
    """
    if current_user.role not in [UserRole.admin, UserRole.superadmin]:
        raise HTTPException(status_code=403, detail="Only admins can view integration status.")

    statuses = {}

    for service in ServiceType:
        success_log = (
            db.query(WebhookLog)
            .filter(WebhookLog.service == service, WebhookLog.status == WebhookStatus.processed)
            .order_by(WebhookLog.created_at.desc())
            .first()
        )

        recent_failure = (
            db.query(WebhookLog)
            .filter(WebhookLog.service == service, WebhookLog.status == WebhookStatus.failed)
            .order_by(WebhookLog.created_at.desc())
            .first()
        )

        if success_log:
            last_success = success_log.created_at.isoformat()
            event_id = success_log.event_id

            if recent_failure and recent_failure.created_at > success_log.created_at:
                status = "degraded"
            else:
                status = "healthy"
        else:
            last_success = None
            event_id = None
            status = "error"

        statuses[service.value] = ServiceIntegrationStatus(
            last_success=last_success,
            last_event_id=event_id,
            status=status,
        )

    return statuses