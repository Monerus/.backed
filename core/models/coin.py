from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base 
from sqlalchemy import ForeignKey, DateTime
from .users import *
from datetime import datetime

class Coin(Base):
    __tablename__ = "coin"
    id: Mapped[int] = mapped_column(primary_key=True)
    gold: Mapped[int] = mapped_column(default=0, nullable=True)
    diamond: Mapped[int] = mapped_column(default=0, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                default=datetime.utcnow,
                                                onupdate=datetime.utcnow)
    level: Mapped[int] = mapped_column(default=0)


class UserCoin(Base):
    __tablename__ = "user_coin"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    coin_id: Mapped[int] = mapped_column(ForeignKey("coin.id"), index=True)

    is_opened: Mapped[bool] = mapped_column(default=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    coin: Mapped["Coin"] = relationship()
    user: Mapped["User"] = relationship()