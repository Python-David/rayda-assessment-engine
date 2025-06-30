from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.enums import ServiceType, WebhookStatus
from app.db.base import Base


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id = Column(String, nullable=False, unique=True)
    service = Column(SqlEnum(ServiceType), nullable=False)
    org_id = Column(String, nullable=False)
    received_at = Column(DateTime, default=datetime.now())
    status = Column(
        SqlEnum(WebhookStatus), default=WebhookStatus.processed, nullable=False
    )
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
