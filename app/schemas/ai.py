from pydantic import BaseModel

class SummaryResponse(BaseModel):
    summary: str
    task_count: int