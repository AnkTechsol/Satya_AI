from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, Base
from .core.audit_logger import AuditLogger

from .routers.policies import router as policies_router
from .routers.agents import router as agents_router
from .routers.audit import router as audit_router
from .routers.evaluate import router as evaluate_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production use Alembic, but good for dev)
    # async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)

    # Start Audit Logger background task
    audit_logger = AuditLogger()
    app.state.audit_logger = audit_logger
    await audit_logger.start()

    yield

    # Shutdown
    await audit_logger.stop()

app = FastAPI(
    title="Satya AI",
    description="Agentic Governance Framework",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(policies_router)
app.include_router(agents_router)
app.include_router(audit_router)
app.include_router(evaluate_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
