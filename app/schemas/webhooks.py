from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr

from app.core.enums import BillingCycle, CommunicationStatus, SubscriptionPlan

# --- Common base event ---


class Metadata(BaseModel):
    source: str
    version: str
    correlation_id: Optional[str] = None
    sales_rep: Optional[str] = None
    gateway: Optional[str] = None
    campaign_id: Optional[str] = None
    notification_type: Optional[str] = None


class BaseWebhookEvent(BaseModel):
    event_type: str
    event_id: str
    timestamp: datetime
    organization_id: str
    metadata: Metadata


# --- User Service Events ---


class UserData(BaseModel):
    user_id: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    department: Optional[str]
    title: Optional[str]
    status: Optional[str]
    hire_date: Optional[str]


class UserCreatedData(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    department: Optional[str] = None
    title: Optional[str] = None
    status: str
    hire_date: Optional[datetime] = None


class UserUpdatedChanges(BaseModel):
    department: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None


class UserUpdatedPrevious(BaseModel):
    department: Optional[str] = None
    title: Optional[str] = None


class UserUpdatedData(BaseModel):
    user_id: str
    changes: UserUpdatedChanges
    previous_values: Optional[UserUpdatedPrevious] = None


class UserDeletedData(BaseModel):
    user_id: str
    email: EmailStr
    deletion_reason: str
    termination_date: Optional[datetime] = None
    data_retention_policy: Optional[str] = None


class UserServiceEvent(BaseWebhookEvent):
    data: UserData


# --- Payment Service Events ---


class SubscriptionCreatedData(BaseModel):
    subscription_id: str
    customer_id: str
    plan: SubscriptionPlan
    status: str
    billing_cycle: Optional[BillingCycle]
    amount: float
    currency: str
    trial_end: Optional[datetime]


class PaymentFailedData(BaseModel):
    payment_id: str
    subscription_id: str
    amount: float
    currency: str
    failure_reason: str
    failure_code: Optional[str] = None
    retry_at: Optional[datetime] = None
    attempt_number: Optional[int] = None


class PaymentServiceEvent(BaseWebhookEvent):
    data: SubscriptionCreatedData | PaymentFailedData


# --- Communication Service Events ---


class MessageDeliveredData(BaseModel):
    message_id: str
    recipient: EmailStr
    template: str
    status: CommunicationStatus
    delivery_time_ms: Optional[int] = None
    esp_message_id: Optional[str] = None


class MessageBouncedData(BaseModel):
    message_id: str
    recipient: EmailStr
    template: str
    bounce_reason: str
    bounce_type: str
    esp_bounce_code: Optional[str] = None


class CommunicationServiceEvent(BaseWebhookEvent):
    data: MessageDeliveredData | MessageBouncedData


# --- Batch wrapper ---


class BatchWebhookEvents(BaseModel):
    events: List[BaseWebhookEvent]
