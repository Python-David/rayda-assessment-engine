from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
