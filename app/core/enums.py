import enum


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    user = "user"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"
    suspended = "suspended"


class AuditAction(str, enum.Enum):
    CREATED_USER = "created_user"
    UPDATED_USER = "updated_user"
    DELETED_USER = "deleted_user"
    CREATED_ORG = "created_org"
    UPDATED_ORG = "updated_org"
    DELETED_ORG = "deleted_org"

    UPDATED_SUBSCRIPTION = "updated_subscription"
    CREATED_SUBSCRIPTION = "created_subscription"
    PAYMENT_FAILED_SUBSCRIPTION = "payment_failed_subscription"

    UPDATED_COMM_LOG = "updated_comm_log"
    CREATED_COMM_LOG = "created_comm_log"


class ServiceType(str, enum.Enum):
    USER = "user_service"
    PAYMENT = "payment_service"
    COMMUNICATION = "communication_service"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    canceled = "canceled"
    trialing = "trialing"
    past_due = "past_due"
    failed = "failed"


class CommunicationStatus(str, enum.Enum):
    delivered = "delivered"
    failed = "failed"
    bounced = "bounced"
    pending = "pending"


class SubscriptionPlan(str, enum.Enum):
    basic = "basic"
    professional = "professional"
    enterprise = "enterprise"


class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    annual = "annual"
    quarterly = "quarterly"


class UserEventType(str, enum.Enum):
    created = "user.created"
    updated = "user.updated"
    deleted = "user.deleted"


class SubscriptionEventType(str, enum.Enum):
    created = "subscription.created"
    updated = "subscription.updated"
    canceled = "subscription.canceled"
    failed = "payment.failed"


class CommunicationEventType(str, enum.Enum):
    delivered = "message.delivered"
    failed = "message.failed"
    bounced = "message.bounced"


class Department(str, enum.Enum):
    engineering = "Engineering"
    product = "Product"
    sales = "Sales"
    marketing = "Marketing"
    hr = "HR"
    finance = "Finance"


class Title(str, enum.Enum):
    engineer = "Engineer"
    product_manager = "Product Manager"
    designer = "Designer"
    sales_rep = "Sales Representative"
    hr_manager = "HR Manager"


class WebhookStatus(str, enum.Enum):
    processed = "processed"
    failed = "failed"
    skipped = "skipped"


class IntegrationHealthStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    error = "error"
