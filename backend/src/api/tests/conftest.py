import pytest
import pytest_asyncio
import os
from httpx import AsyncClient, ASGITransport

os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_ci")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("MAIL_USERNAME", "test")
os.environ.setdefault("MAIL_PASSWORD", "test")
os.environ.setdefault("MAIL_FROM", "test@example.com")

from main import app
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from models import Base
from auth import create_access_token
from datetime import timedelta

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")


@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def auth_headers(client):
    await client.post("/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "password123"
    })

    res = await client.post("/token", data={
        "username": "testuser",
        "password": "password123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
