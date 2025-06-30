import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.core.auth import get_password_hash
from app.core.config import settings
from app.core.enums import Department, Title, UserRole, UserStatus
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.organization import Organization
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


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()

    # Optional: reset tables
    db.execute(text("TRUNCATE TABLE audit_logs RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE organizations RESTART IDENTITY CASCADE;"))
    db.commit()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.main import limiter

    limiter._storage.reset()


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
    user = (
        db_session.query(User)
        .filter_by(email=settings.INITIAL_SUPERADMIN_EMAIL)
        .first()
    )
    if user is None:
        hashed_pw = get_password_hash(settings.INITIAL_SUPERADMIN_PASSWORD)
        user = User(
            email=settings.INITIAL_SUPERADMIN_EMAIL,
            hashed_password=hashed_pw,
            role=UserRole.superadmin,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def initial_admin_user(db_session, test_org):
    user = db_session.query(User).filter_by(email=settings.INITIAL_ADMIN_EMAIL).first()
    if user is None:
        hashed_pw = get_password_hash(settings.INITIAL_ADMIN_PASSWORD)
        user = User(
            email=settings.INITIAL_ADMIN_EMAIL,
            hashed_password=hashed_pw,
            role=UserRole.admin,
            org_id=test_org.id,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def test_org(db_session):
    org = db_session.query(Organization).filter_by(slug="org_001").first()
    if org is None:
        org = Organization(
            name="DavidOrg",
            slug="org_001",
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
    return org


@pytest_asyncio.fixture()
async def test_user(db_session, test_org):
    user = db_session.query(User).filter_by(external_id="cust_sync_001").first()
    if user is None:
        user = User(
            external_id="cust_sync_001",
            email="customer@example.com",
            first_name="Customer",
            last_name="Example",
            hashed_password=get_password_hash("test_user_password"),
            role=UserRole.user,
            status=UserStatus.active,
            department=Department.finance,
            title=Title.hr_manager,
            org_id=test_org.id,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user
