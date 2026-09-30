from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.task import task_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(task_router)

@app.get("/")
async def home():
    return {"message": "Welcome to production style backend system"}

@app.get("/health")
async def health():
    return {"message": "ok"}