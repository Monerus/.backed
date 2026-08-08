from sqlalchemy.orm import mapped_column, Mapped
from .base import Base
from datetime import datetime
import uuid
from sqlalchemy import UUID, DateTime


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[int] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    code_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    score: Mapped[int] = mapped_column(default=0, index=True)
    diamond: Mapped[int] = mapped_column(default=100)
    gold: Mapped[int] = mapped_column(default=100)