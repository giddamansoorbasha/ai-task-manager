from pydantic import BaseModel

class TaskRequest(BaseModel):
    title: str
    description: str

class TaskResponse(BaseModel): 
    task_id: int 
    title: str 
    description: str 
    user_id: int