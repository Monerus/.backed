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

    user_assignments: Mapped[list["UserTask"]] = relationship(
        "UserTask", 
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
class UserTask(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    current_step: Mapped[int] = mapped_column(default=0)

    # Связи (Relationships)
    task: Mapped["Task"] = relationship("Task", back_populates="user_assignments")
    # Убедись, что в модели User есть tasks: Mapped[list["UserTask"]] = relationship(back_populates="user")
    user: Mapped["Users"] = relationship("User", back_populates="tasks")