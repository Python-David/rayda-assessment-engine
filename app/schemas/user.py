from pydantic import BaseModel, EmailStr
from uuid import UUID

from app.core.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserRead(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreateInOrg(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.admin
