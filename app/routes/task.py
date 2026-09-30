from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.task import Task

from app.schemas.task import TaskRequest, TaskResponse

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])

# create task
@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    new_task = Task(title=task_data.title,description=task_data.description,user_id=current_user.user_id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

# read all tasks
@task_router.get("/", response_model=list[TaskResponse])
async def get_tasks(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Task).where(Task.user_id == current_user.user_id))
    tasks = result.scalars().all()
    return tasks

# read one task
@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Task).where(Task.task_id == task_id,Task.user_id == current_user.user_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Task not found")
    return task

# update task
@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    
    result = await db.execute(select(Task).where(Task.task_id == task_id, Task.user_id == current_user.user_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Task not found")
    task.title = task_data.title
    task.description = task_data.description
    await db.commit()
    await db.refresh(task)
    return task

# delete task
@task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    
    result = await db.execute(select(Task).where(Task.task_id == task_id, Task.user_id == current_user.user_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return None