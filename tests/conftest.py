import os

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://<user>:<password>@localhost:5432/ai_task_manager_test",
)
assert "test" in TEST_DATABASE_URL, "Refusing to run tests on a non-test database"

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-characters-long")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import app.models.user as _user_model  # noqa: F401  (registers tables on Base)
import app.models.task as _task_model  # noqa: F401
from app.core.database import Base, get_async_db
from app.main import app


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_async_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
def login_as(client):
    async def _login(email: str = "a@test.com", password: str = "Pass1234!"):
        await client.post("/auth/signup", json={"name": "Test", "email": email, "password": password})
        res = await client.post("/auth/login", data={"username": email, "password": password})
        return {"Authorization": f"Bearer {res.json()['access_token']}"}
    return _login