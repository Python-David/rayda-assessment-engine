from pydantic import BaseModel, EmailStr
from uuid import UUID

class OrgBase(BaseModel):
    name: str
    slug: str

class OrgCreate(BaseModel):
    name: str
    slug: str
    initial_admin_email: EmailStr
    initial_admin_password: str

class OrgRead(OrgBase):
    id: UUID

    class Config:
        from_attributes = True
