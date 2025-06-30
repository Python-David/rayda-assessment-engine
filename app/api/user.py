from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import (
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from app.core.enums import AuditAction, UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreateInOrg, UserRead
from app.utils.audit import log_audit

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_user_in_org(
    user_in: UserCreateInOrg,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new user (or admin) within the current organization.

    Only accessible by admins.

    Args:
        user_in: User creation input schema.
        db: Database session dependency.
        current_user: Current authenticated admin user.

    Returns:
        The newly created user as UserRead schema.

    Raises:
        HTTPException: If current user is not an admin.
        HTTPException: If the role provided is invalid.
        HTTPException: If email is already registered.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admins can create users.")

    if user_in.role not in [UserRole.user, UserRole.admin]:
        raise HTTPException(
            status_code=400, detail="Invalid role. Must be 'user' or 'admin'."
        )

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    new_user = User(
        id=uuid4(),
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole(user_in.role),
        org_id=current_user.org_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit(db, AuditAction.CREATED_USER, current_user.id, current_user.org_id)

    return new_user


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT access token.

    Args:
        form_data: OAuth2 form data containing username and password.
        db: Database session dependency.

    Returns:
        A JSON object containing the access token and token type.

    Raises:
        HTTPException: If credentials are invalid.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_active_user)) -> UserRead:
    """
    Retrieve the currently authenticated user's profile.

    Args:
        current_user: Current authenticated user dependency.

    Returns:
        The user's profile data as UserRead schema.
    """
    return current_user
