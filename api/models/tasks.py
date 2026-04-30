from pydantic import BaseModel, ConfigDict
from uuid import UUID

class TasksBase(BaseModel):
    title: str
    reward: int
    # step: int
    last_step: int

class TasksCreate(TasksBase):
    pass

class TasksResponse(TasksBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
    