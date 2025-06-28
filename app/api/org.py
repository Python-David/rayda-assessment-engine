from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.core.auth import get_current_active_user, get_password_hash
from app.core.enums import UserRole
from app.models.user import User
from app.schemas.organization import OrgCreate, OrgRead
from app.db.session import get_db
from app.models.organization import Organization

router = APIRouter()

@router.post("/", response_model=OrgRead)
def create_org(
    org_in: OrgCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin can create organizations.")

    existing = db.query(Organization).filter(Organization.slug == org_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this slug already exists.")

    org = Organization(id=uuid4(), name=org_in.name, slug=org_in.slug)
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create initial admin user for this org
    admin_user = User(
        id=uuid4(),
        email=org_in.initial_admin_email,
        hashed_password=get_password_hash(org_in.initial_admin_password),
        role=UserRole.admin,
        org_id=org.id,
    )
    db.add(admin_user)
    db.commit()

    return org


@router.get("/{org_id}", response_model=OrgRead)
def get_org(org_id: UUID, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
