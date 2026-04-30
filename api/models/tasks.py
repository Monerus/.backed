from pydantic import BaseModel, ConfigDict

class TasksBase(BaseModel):
    title: str
    reward: int
    last_step: int

class TasksCreate(TasksBase):
    pass

class TasksResponse(TasksBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserTaskResponse(BaseModel):
    id: int
    task_id: int 
    title: str
    step: int
    last_step: int
    completed: bool
    user_id: int
    model_config = ConfigDict(from_attributes=True)
    