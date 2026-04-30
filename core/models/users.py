from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    score: Mapped[int] = mapped_column(default=0, index=True)
    diamond: Mapped[int] = mapped_column(default=100)
    gold: Mapped[int] = mapped_column(default=100)