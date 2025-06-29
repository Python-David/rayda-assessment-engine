import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.core.auth import get_password_hash
from app.core.enums import UserRole
from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.core.config import settings
from app.models.user import User

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    create_database(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    drop_database(TEST_DATABASE_URL)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest_asyncio.fixture()
async def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
async def superadmin_user(db_session):
    user = db_session.query(User).filter_by(email=settings.INITIAL_SUPERADMIN_EMAIL).first()
    if user is None:
        hashed_pw = get_password_hash(settings.INITIAL_SUPERADMIN_PASSWORD)
        user = User(
            email=settings.INITIAL_SUPERADMIN_EMAIL,
            hashed_password=hashed_pw,
            role=UserRole.superadmin
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def initial_admin_user(db_session):
    user = db_session.query(User).filter_by(email=settings.INITIAL_ADMIN_EMAIL).first()
    if user is None:
        hashed_pw = get_password_hash(settings.INITIAL_ADMIN_PASSWORD)
        user = User(
            email=settings.INITIAL_ADMIN_EMAIL,
            hashed_password=hashed_pw,
            role=UserRole.admin
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

