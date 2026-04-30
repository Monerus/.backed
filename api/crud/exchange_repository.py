from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from api.crud.auth_utils import *


router = APIRouter(prefix="/exchange", tags=["Exchange"])


#Создать обмен
@router.post("/")
async def create_exchange(
        recipient_id: int,
        sender_card_id: int,
        recipient_card_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user: Users = Depends(get_current_user)):
    
    if recipient_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Нельзя обмениваться с собой")
    
    result = await session.execute(
        select(UserCards).where(
            UserCards.user_id == current_user.id,
            UserCards.cards_id == sender_card_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="У тебя нет этой карты")
    

    result = await session.execute(
        select(UserCards).where(
            UserCards.user_id == recipient_id,
            UserCards.cards_id == recipient_card_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="У получателя нет этой карты")

    exchange = CardExchange(
        sender_id = current_user.id,
        recipient_id = recipient_id,
        sender_card_id = sender_card_id,
        recipient_card_id = recipient_card_id,
        status=ExchangeStatus.pending
    )

    session.add(exchange)
    await session.commit()

    return {"message": "Обмен предложен"}


# Принять обмен
@router.post("/{exchange_id}/accept/")
async def accept_exchange(
    exchange_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: Users = Depends(get_current_user)
):
    result = await session.execute(
        select(CardExchange).where(CardExchange.id == exchange_id)
    )
    exchange = result.scalar_one_or_none()

    if not exchange:
        raise HTTPException(404, "Обмен не найден")

    if exchange.recipient_id != current_user.id:
        raise HTTPException(403, "Не твой обмен")

    if exchange.status != ExchangeStatus.pending:
        raise HTTPException(400, "Уже обработан")

    # проверка владения картами
    sender_card = await session.execute(
        select(UserCards).where(
            UserCards.user_id == exchange.sender_id,
            UserCards.cards_id == exchange.sender_card_id
        )
    )

    recipient_card = await session.execute(
        select(UserCards).where(
            UserCards.user_id == exchange.recipient_id,
            UserCards.cards_id == exchange.recipient_card_id
        )
    )

    sender_card = sender_card.scalar_one_or_none()
    recipient_card = recipient_card.scalar_one_or_none()

    if not sender_card or not recipient_card:
        raise HTTPException(400, "Одна из карт уже отсутствует")

    # обмен (меняем владельцев)
    sender_card.user_id = exchange.recipient_id
    recipient_card.user_id = exchange.sender_id

    exchange.status = ExchangeStatus.accepted

    await session.commit()

    return {"message": "Обмен завершён"}