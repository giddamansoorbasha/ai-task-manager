import logging
from contextlib import asynccontextmanager

import app.core.logging as _app_logging  # noqa: F401
from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.task import task_router
from app.routes.ai import ai_router


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application stopped")


app = FastAPI(title="AI Task Manager", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(ai_router)

@app.get("/")
async def home():
    return {"message": "Welcome to production style backend system"}

@app.get("/health")
async def health():
    return {"status": "ok"}