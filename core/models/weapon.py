from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from sqlalchemy import ForeignKey, JSON, String

class Weapon(Base): # Equipment
    __tablename__ = "weapon"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    level: Mapped[int] = mapped_column(default=1)
    damage: Mapped[int] = mapped_column(default=1) 
    #Кирка наносит +1 урон. А от шлема и костюма отнимается что-то(сколько-то зависит от температуры?)?
    improvement: Mapped[int] = mapped_column(default=200)


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    item_type: Mapped[str] = mapped_column(String(50))

    level: Mapped[int] = mapped_column(default=1)
    improvement: Mapped[int] = mapped_column(default=20)

    stats: Mapped[dict] = mapped_column(JSON, default={})



    