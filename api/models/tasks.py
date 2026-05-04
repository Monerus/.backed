from pydantic import BaseModel, ConfigDict
from datetime import datetime
from core.models import *

class TasksBase(BaseModel):
    title: str
    reward: int
    last_step: int
    task_type: TaskType

class TasksResponse(TasksBase):
    id: int
    title: str
    reward: int
    last_step: int
    task_type: TaskType
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserTaskResponse(BaseModel):
    id: int
    task_id: int
    title: str

    step: int
    last_step: int

    completed: bool
    reward: int
    reward_claimed: bool

    model_config = ConfigDict(from_attributes=True)
    