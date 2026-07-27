import os

import pytest_asyncio
from dotenv import dotenv_values
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine


# The application builds its engine while modules are imported. Point it to the
# isolated test database before importing anything from app.
env = dotenv_values(".env")
source_database_url = make_url(str(env["DATABASE_URL"])).set(host="127.0.0.1")
database_url = source_database_url.set(
    host="127.0.0.1",
    database="back_routine_test",
)
os.environ["DATABASE_URL"] = database_url.render_as_string(hide_password=False)
os.environ["APP_ENV"] = "test"
os.environ["RATE_LIMIT_STORAGE_URI"] = ""

import app.models  # noqa: E402, F401
from app.api.dependencies import get_session  # noqa: E402
from app.api.main import app  # noqa: E402
from app.db.db import Base, async_session_maker, engine  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    admin_engine = create_async_engine(
        source_database_url.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
    )
    async with admin_engine.connect() as connection:
        exists = await connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": "back_routine_test"},
        )
        if not exists:
            await connection.execute(text("CREATE DATABASE back_routine_test"))
    await admin_engine.dispose()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session():
    async with async_session_maker() as test_session:
        yield test_session


@pytest_asyncio.fixture
async def client(session):
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    app.state.limiter.enabled = False

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()
