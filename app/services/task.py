from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.task import Task

async def select_task(db: AsyncSession):
    pass

async def select_tasks(db: AsyncSession):
    pass

async def insert_task(db: AsyncSession):
    pass

async def update_task(db: AsyncSession):
    pass

async def delete_task(db: AsyncSession):
    pass