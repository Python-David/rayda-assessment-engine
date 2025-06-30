from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, get_password_hash
from app.core.enums import AuditAction, UserRole
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrgCreate, OrgRead
from app.utils.audit import log_audit

router = APIRouter()


@router.post("/", response_model=OrgRead)
def create_org(
    org_in: OrgCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new organization and its initial admin user.

    Only accessible by superadmins.

    Steps:
    - Validates slug uniqueness.
    - Creates the organization.
    - Logs the organization creation in audit logs.
    - Creates an initial admin user for the new organization.
    - Logs the admin user creation in audit logs.

    Args:
        org_in: Organization creation input schema.
        db: Database session dependency.
        current_user: Current authenticated user.

    Returns:
        The created organization as OrgRead schema.
    """
    if current_user.role != UserRole.superadmin:
        raise HTTPException(
            status_code=403, detail="Only superadmin can create organizations."
        )

    existing = db.query(Organization).filter(Organization.slug == org_in.slug).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Organization with this slug already exists."
        )

    org = Organization(id=uuid4(), name=org_in.name, slug=org_in.slug)
    db.add(org)
    db.commit()
    db.refresh(org)

    log_audit(db, AuditAction.CREATED_ORG, current_user.id, org.id)

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

    log_audit(db, AuditAction.CREATED_USER, current_user.id, org.id)

    return org


@router.get("/{org_id}", response_model=OrgRead)
def get_org(org_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific organization by its ID.

    This endpoint is publicly accessible (no authentication required).

    Args:
        org_id: UUID of the organization to retrieve.
        db: Database session dependency.

    Returns:
        The organization details as OrgRead schema.

    Raises:
        HTTPException: If organization is not found.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
