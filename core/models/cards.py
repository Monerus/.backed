from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from sqlalchemy import ForeignKey

class SetCards(Base):
    __tablename__ = "set_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int]


class Cards(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str]
    text: Mapped[str]
    title: Mapped[str]
    set_id: Mapped[int] = mapped_column(ForeignKey("set_cards.id"))


#Демо! Покупка карточек.
class UserCards(Base):
    __tablename__ = "user_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cards_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))


# class ExchangeStatus(enum.Enum):
#     pending = "pending"
#     accepted = "accepted"
#     declined = "declined"

# # Обмен карточками между пользователями.
# class CardExchange(Base):
#     __tablename__ = "card_exchange"
    
#     id: Mapped[int] = mapped_column(primary_key=True)

#     sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

#     sender_card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
#     recipient_card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))

#     status: Mapped[ExchangeStatus]
    
