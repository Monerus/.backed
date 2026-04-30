from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .base import Base
from .users import *

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True) 
    title: Mapped[str] = mapped_column(nullable=False)
    last_step: Mapped[int] = mapped_column(default=0)
    reward: Mapped[int] = mapped_column(default=0)

    
class UserTask(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))

    task: Mapped["Task"] = relationship()
    user: Mapped["Users"] = relationship()

    step: Mapped[int] = mapped_column(default=0)

    completed: Mapped[bool] = mapped_column(default=False)
    reward_claimed: Mapped[bool] = mapped_column(default=False)

