from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.enums import CommunicationStatus
from app.db.base import Base

class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(CommunicationStatus), nullable=False)
    template = Column(String, nullable=True)
    delivery_time_ms = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
