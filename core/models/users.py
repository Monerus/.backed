from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import UUID

if TYPE_CHECKING:
    from .task import UserTask

class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    score: Mapped[int] = mapped_column(default=0, index=True)
    diamond: Mapped[int] = mapped_column(default=100)
    gold: Mapped[int] = mapped_column(default=100)
    tasks: Mapped[list["UserTask"]] = relationship(back_populates="user")