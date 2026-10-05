import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.ai import SummaryResponse
from app.services.ai import AIServiceError, AITimeoutError, summarize_tasks

logger = logging.getLogger(__name__)
ai_router = APIRouter(prefix="/ai", tags=["AI"])


@ai_router.post("/summary", response_model=SummaryResponse)
async def summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user.user_id, Task.status != TaskStatus.done)
        .order_by(Task.due_date.asc().nulls_last(), Task.task_id)
        .limit(50)
    )
    tasks = result.scalars().all()

    if not tasks:
        return SummaryResponse(summary="You have no open tasks.", task_count=0)

    try:
        text = await summarize_tasks(tasks)
    except AITimeoutError:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI request timed out")
    except AIServiceError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")

    logger.info("AI summary created task_count=%s user_id=%s", len(tasks), current_user.user_id)
    return SummaryResponse(summary=text, task_count=len(tasks))