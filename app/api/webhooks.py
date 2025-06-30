from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.webhooks import (
    UserServiceEvent,
    PaymentServiceEvent,
    CommunicationServiceEvent,
    BatchWebhookEvents,
)
from app.services.tasks import process_event
from app.core.enums import ServiceType

router = APIRouter()

def enqueue_event(event: dict, service_enum: ServiceType):
    try:
        process_event.apply_async((event, service_enum.value), queue="integration_queue")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user-service")
@limiter.limit(settings.webhook_rate_limit)
async def user_service_webhook(request: Request, payload: UserServiceEvent | BatchWebhookEvents):
    service_enum = ServiceType.USER

    match payload:
        case BatchWebhookEvents(events=events):
            for event in events:
                enqueue_event(event.model_dump(), service_enum)
        case UserServiceEvent():
            enqueue_event(payload.model_dump(), service_enum)
        case _:
            raise HTTPException(status_code=400, detail="Invalid payload type")

    return JSONResponse(content={"status": "received"}, status_code=202)


@router.post("/payment-service")
@limiter.limit(settings.webhook_rate_limit)
async def payment_service_webhook(request: Request, payload: PaymentServiceEvent | BatchWebhookEvents):
    service_enum = ServiceType.PAYMENT

    match payload:
        case BatchWebhookEvents(events=events):
            for event in events:
                enqueue_event(event.model_dump(), service_enum)
        case PaymentServiceEvent():
            enqueue_event(payload.model_dump(), service_enum)
        case _:
            raise HTTPException(status_code=400, detail="Invalid payload type")

    return JSONResponse(content={"status": "received"}, status_code=202)

@router.post("/communication-service")
@limiter.limit(settings.webhook_rate_limit)
async def communication_service_webhook(request: Request, payload: CommunicationServiceEvent | BatchWebhookEvents):
    service_enum = ServiceType.COMMUNICATION

    match payload:
        case BatchWebhookEvents(events=events):
            for event in events:
                enqueue_event(event.model_dump(), service_enum)
        case CommunicationServiceEvent():
            enqueue_event(payload.model_dump(), service_enum)
        case _:
            raise HTTPException(status_code=400, detail="Invalid payload type")

    return JSONResponse(content={"status": "received"}, status_code=202)
