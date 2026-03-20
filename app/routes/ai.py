from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.task import Task
from app.services.ai_service import summarize_tasks
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["AI"])
limiter = Limiter(key_func=get_remote_address)

class SummaryResponse(BaseModel):
    summary: str
    task_count: int

@router.post("/ai-summary", response_model=SummaryResponse)
@limiter.limit("5/minute")
def get_ai_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this user")

    summary = summarize_tasks(tasks)

    return {
        "summary": summary,
        "task_count": len(tasks)
    }