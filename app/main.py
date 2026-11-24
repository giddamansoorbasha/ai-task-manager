from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.task import task_router
from app.core.database import Base, async_engine
from app.models.user import User
from app.models.task import Task

async def reset_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(_: FastAPI):
    print("🟢 Application started...")
    await reset_db()
    yield
    print("🔴 Application stopped...")

app = FastAPI(title="AI Task Manager", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(task_router)

@app.get("/")
async def home():
    return {"message": "Welcome to production style backend-system"}

@app.get("/health")
async def health():
    return {"status": "ok"}