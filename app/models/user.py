import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.enums import Department, Title, UserRole, UserStatus
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    department = Column(Enum(Department), nullable=True)
    title = Column(Enum(Title), nullable=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    external_id = Column(String, unique=True, index=True, nullable=True)
