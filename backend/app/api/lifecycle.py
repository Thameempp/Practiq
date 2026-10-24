from contextlib import asynccontextmanager

from app.orchestration.service import close_orchestrator


@asynccontextmanager
async def lifespan(app):
    try:
        yield
    finally:
        close_orchestrator()
