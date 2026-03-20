from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import StatusEnum, PriorityEnum

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = PriorityEnum.medium

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: StatusEnum
    priority: PriorityEnum
    created_at: datetime

    class Config:
        from_attributes = True