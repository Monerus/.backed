from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from api.crud.auth_utils import *
from api.crud.task_utils import *


router = APIRouter(prefix='/coin', tags=["Coin"])


# Создание монет(админ)
@router.post('/create/', response_model=CoinResponse)
async def create_coin(
    coin_in: CoinBase,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    coin = Coin(**coin_in.model_dump())

    try:
        session.add(coin)
        await session.commit()
        await session.refresh(coin)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error: {e}"
        )
    return coin


# Показ всех монет(админ)
@router.get("/get-coins/")
async def get_coins(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(select(Coin))
    stmt = result.scalars().all()
    return stmt

#Выдача монеты пользователю(монета рандомная)
@router.post("/add-coin/")
async def add_coin_to_user(current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):

    stmt = select(Coin.id).where(
        Coin.id.not_in(
            select(UserCoin.coin_id).where(UserCoin.user_id == current_user.id)
        )
    ).order_by(func.random()).limit(1)

    result = await session.execute(stmt)
    random_coin_id = result.scalar_one_or_none()


    new_coin = UserCoin(
        user_id = current_user.id,
        coin_id = random_coin_id,
        is_opened = False
    )

    if not random_coin_id:
        raise HTTPException(status_code=404, detail="Вы собрали все доступные монеты!")
    
    session.add(new_coin)

    try:
        await session.commit()
        await session.refresh(new_coin)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка покупки: {e}"
        )
    return new_coin

#открытие монет.
@router.post("/here-the-reward/")
async def here_reward(coin_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    
    result = await session.execute(
        select(UserCoin).where(
            UserCoin.user_id == current_user.id,
            UserCoin.coin_id == coin_id
        )
    )

    user_coin = result.scalar_one_or_none()

    if not user_coin:
        raise HTTPException(status_code=404, detail="У вас нет такой монеты")
    
    if user_coin.is_opened:
        raise HTTPException(status_code=400, detail="Награда уже получена")
    
    user_coin.is_opened = True
    user_coin.opened_at = datetime.utcnow()

    coin_data = await session.execute(select(Coin).where(Coin.id == coin_id))
    coin = coin_data.scalar_one()
    current_user.gold += coin.gold

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении")
    
    return {"message": "Успешно", "gold": coin.gold}