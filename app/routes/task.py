import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskRequest, TaskResponse, TaskStatusUpdate

logger = logging.getLogger(__name__)
task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def get_user_task_or_404(db: AsyncSession, task_id: int, user_id: int) -> Task:
    result = await db.execute(select(Task).where(Task.task_id == task_id, Task.user_id == user_id))
    task = result.scalar_one_or_none()
    if task is None:
        logger.warning("Task not found task_id=%s user_id=%s", task_id, user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        user_id=current_user.user_id,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    logger.info("Task created task_id=%s user_id=%s", new_task.task_id, current_user.user_id)
    return new_task


@task_router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    status_filter: TaskStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Task).where(Task.user_id == current_user.user_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    query = query.order_by(Task.due_date.asc().nulls_last(), Task.task_id).limit(limit).offset(offset)
    result = await db.execute(query)
    tasks = result.scalars().all()
    logger.info("Tasks fetched count=%s limit=%s offset=%s user_id=%s", len(tasks), limit, offset, current_user.user_id)
    return tasks


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    return await get_user_task_or_404(db, task_id, current_user.user_id)


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    task = await get_user_task_or_404(db, task_id, current_user.user_id)
    task.title = task_data.title
    task.description = task_data.description
    task.due_date = task_data.due_date
    await db.commit()
    await db.refresh(task)
    logger.info("Task updated task_id=%s user_id=%s", task_id, current_user.user_id)
    return task


@task_router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(task_id: int, body: TaskStatusUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    task = await get_user_task_or_404(db, task_id, current_user.user_id)
    task.status = body.status
    await db.commit()
    await db.refresh(task)
    logger.info("Task status task_id=%s status=%s user_id=%s", task_id, body.status.value, current_user.user_id)
    return task


@task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    task = await get_user_task_or_404(db, task_id, current_user.user_id)
    await db.delete(task)
    await db.commit()
    logger.info("Task deleted task_id=%s user_id=%s", task_id, current_user.user_id)