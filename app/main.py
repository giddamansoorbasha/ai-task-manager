from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import User, Task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Task Manager")

@app.get("/")
def root():
    return {"message": "Ai Task Manager API is running"}

