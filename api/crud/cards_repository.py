from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from typing import List
from api.crud.auth_utils import *

router = APIRouter(prefix="/cards", tags=["Cards"])

# Создаем карточки.
@router.post("/create/", response_model=CardsResponse)
async def create_cards(card_in: CardsCreate,
                       session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    card = Cards(**card_in.model_dump())
    try:
        session.add(card)
        await session.commit()
        await session.refresh(card)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error: {e}")
    return card

# Показываем все карточки.
@router.get("/get-cards/", response_model=List[CardsResponse])
async def get_cards(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(
        select(Cards)
        .order_by(Cards.set_id))
    stmt = result.scalars().all()
    return stmt


#Создаем наборы карточек.
@router.post("/categories/cards/", response_model=SetCardsResponse)
async def create_setcards(set_cards_in: SetCardsCreate, 
                         session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    categories = SetCards(**set_cards_in.model_dump())
    try:
        session.add(categories)
        await session.commit()
        await session.refresh(categories)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка: {e}")
    return categories


# Показываем все наборы.
@router.get("/set-cards/", response_model=List[SetCardsResponse])
async def get_cards(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(
        select(SetCards))
    stmt = result.scalars().all()
    return stmt

# Покупка карт(пока что, в будущем получать их в рандомный момент игры.)
@router.post("/card/{card_id}/")
async def buy_cards(
    card_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_user)
):
    # Получаем карточку
    result = await session.execute(
        select(Cards).where(Cards.id == card_id)
    )
    card = result.scalar_one_or_none()

    # Проверка: существует ли карточка
    if not card:
        raise HTTPException(
            status_code=404,
            detail="Карточка не найдена"
        )

    # Проверка: уже куплена или нет
    existing = await session.execute(
        select(UserCards).where(
            UserCards.user_id == current_user.id,
            UserCards.cards_id == card_id
        )
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Карточка уже куплена"
        )

    # Добавляем карточку пользователю
    user_card = UserCards(
        user_id=current_user.id,
        cards_id=card.id
    )

    session.add(user_card)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка: {e}"
        )

    return {"message": "Карточка получена"}

