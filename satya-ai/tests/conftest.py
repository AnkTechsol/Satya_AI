import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from satya.database import Base, get_db
from satya.main import app
from httpx import AsyncClient, ASGITransport
from satya.core.audit_logger import AuditLogger

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    # Needs to be a fresh memory DB per test so things don't clash, but more importantly,
    # we need the same engine for the override and the mock. Let's use file memory DB to share it across threads
    # because aiosqlite :memory: is per-connection by default.
    engine = create_async_engine("sqlite+aiosqlite:///file:memdb1?mode=memory&cache=shared", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    AsyncSessionLocal = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client(db_engine, db_session, monkeypatch):
    AsyncSessionLocalTest = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async def override_get_db():
        async with AsyncSessionLocalTest() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # We must also mock AsyncSessionLocal used in AgentRegistry and AuditLogger
    monkeypatch.setattr("satya.core.agent_registry.AsyncSessionLocal", AsyncSessionLocalTest)
    monkeypatch.setattr("satya.core.audit_logger.AsyncSessionLocal", AsyncSessionLocalTest)

    audit_logger = AuditLogger()
    app.state.audit_logger = audit_logger
    await audit_logger.start()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.headers["X-Satya-Key"] = "DEMO_KEY"
        yield ac

    await audit_logger.stop()
    app.dependency_overrides.clear()
