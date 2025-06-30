from uuid import uuid4

from app.core.auth import get_password_hash
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.utils.logger import get_logger

logger = get_logger("bootstrap")


def create_initial_superadmin():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            email = settings.INITIAL_SUPERADMIN_EMAIL
            password = settings.INITIAL_SUPERADMIN_PASSWORD
            if not email or not password:
                raise RuntimeError(
                    "INITIAL_SUPERADMIN_EMAIL and INITIAL_SUPERADMIN_PASSWORD must be set in .env"
                )

            super_admin = User(
                id=uuid4(),
                email=email,
                hashed_password=get_password_hash(password),
                role=UserRole.superadmin,
                org_id=None,
            )
            db.add(super_admin)
            db.commit()

            logger.info("Initial Super Admin created.")

        else:
            logger.info("Superadmin already exists. Skipping creation.")

    except Exception as e:
        logger.error(f"Error creating superadmin: {e}")
        raise
    finally:
        db.close()
