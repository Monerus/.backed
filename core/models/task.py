from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Date, Enum
from .base import Base
from .users import *
from datetime import datetime, date
import enum

class TaskType(enum.Enum):
    PERMANENT = "permanent"
    DAILY = "daily"
    WEEKLY = "weekly"


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True) 
    title: Mapped[str] = mapped_column(nullable=False)
    last_step: Mapped[int] = mapped_column(default=0)
    reward: Mapped[int] = mapped_column(default=0)
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), 
        default=TaskType.PERMANENT
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, 
                                                 default=datetime.utcnow, 
                                                 onupdate=datetime.utcnow
                                                )
    
class UserTask(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)

    task: Mapped["Task"] = relationship()
    user: Mapped["Users"] = relationship()

    step: Mapped[int] = mapped_column(default=0)

    completed: Mapped[bool] = mapped_column(default=False)
    reward_claimed: Mapped[bool] = mapped_column(default=False)

    last_reset_date: Mapped[date] = mapped_column(Date, 
                                                  default=date.today
                                                  )

