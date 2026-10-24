from pydantic import BaseModel, AwareDatetime, Field
from app.models.task import TaskStatus
from app.models.task import TaskPriority, TaskStatus

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    priority: TaskPriority | None = None
    due_date: AwareDatetime | None = None

class TaskResponse(BaseModel):
    task_id: int
    title: str
    description: str
    user_id: int
    status: TaskStatus
    priority: TaskPriority
    due_date: AwareDatetime | None = None