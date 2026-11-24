from pydantic import BaseModel, AwareDatetime, Field, ConfigDict
from app.models.task import TaskPriority, TaskStatus
from uuid import UUID

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    priority: TaskPriority | None = None
    due_date: AwareDatetime | None = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    title: str
    description: str
    user_id: UUID
    status: TaskStatus
    priority: TaskPriority
    due_date: AwareDatetime | None = None