from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExternalUserData(BaseModel):
    user_id: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    department: Optional[str]
    title: Optional[str]
    status: str
    manager_id: Optional[str]
    hire_date: Optional[str]
    last_updated: Optional[datetime]

class ExternalUserSuccessResponse(BaseModel):
    status: str
    data: ExternalUserData

class ExternalUserErrorResponse(BaseModel):
    status: str
    error_code: str
    message: str
    timestamp: datetime

class ExternalUserSummary(BaseModel):
    user_id: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    status: str

class Pagination(BaseModel):
    total: int
    page: int
    per_page: int
    has_more: bool

class ExternalUserListData(BaseModel):
    users: List[ExternalUserSummary]
    pagination: Pagination

class ExternalUserListSuccessResponse(BaseModel):
    status: str
    data: ExternalUserListData

class ExternalSubscriptionData(BaseModel):
    subscription_id: str
    customer_id: str
    plan: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    amount: float
    currency: str
    payment_method: Optional[str]

class ExternalSubscriptionSuccessResponse(BaseModel):
    status: str
    data: ExternalSubscriptionData

class ExternalSubscriptionErrorResponse(BaseModel):
    status: str
    error_code: str
    message: str
    timestamp: datetime

class ExternalCustomerUsageMetrics(BaseModel):
    api_calls: int
    storage_gb: float
    compute_hours: float

class ExternalCustomerUsageData(BaseModel):
    customer_id: str
    billing_period: str
    usage_metrics: ExternalCustomerUsageMetrics
    overage_charges: float
    total_amount: float

class ExternalCustomerUsageSuccessResponse(BaseModel):
    status: str
    data: ExternalCustomerUsageData

class ExternalMessageData(BaseModel):
    message_id: str
    status: str
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

class ExternalMessageSuccessResponse(BaseModel):
    status: str
    data: ExternalMessageData

class ExternalMessageErrorResponse(BaseModel):
    status: str
    error_code: str
    message: str
    timestamp: datetime