from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import User, Task
from app.routes import auth, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Task Manager")

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "AI Task Manager API is running"}