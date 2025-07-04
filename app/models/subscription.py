import uuid

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.enums import BillingCycle, SubscriptionPlan
from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    external_subscription_id = Column(String, unique=True, index=True, nullable=False)
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    status = Column(String, nullable=False)
    billing_cycle = Column(Enum(BillingCycle), nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    trial_end = Column(DateTime, nullable=True)
