import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.enums import AuditAction
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    action = Column(Enum(AuditAction), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
