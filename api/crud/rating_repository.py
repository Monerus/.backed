from api.models import *
from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import Depends, APIRouter
from api.crud.auth_utils import *

router = APIRouter(prefix='/rating', tags=["Rating"])


# Показать рейтинг, только имя и счетчик 
@router.get("/")
async def get_rating_users(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    
    result = await session.execute(
        select(User.id, User.score)
        .order_by(desc(User.score))
        .limit(200))
    
    stmt = result.mappings().all()
    return stmt


@router.get("/me/")
async def get_my_rating(session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                        current_user: User = Depends(get_current_user)):
    
    query_rank = select(
        func.count(User.id)
        ).where(User.score > current_user.score)

    result = await session.execute(query_rank)

    rank = result.scalar_one() + 1
    
    return {
        "name": current_user.id,
        "score": current_user.score
    }
    

# Считать шаги и записывать их в базу данных
@router.post('/score')
async def save_score(data: UserScore,
                     current_user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(db_helper.scoped_session_dependency)): 
    
    if data.score > current_user.score:
        current_user.score = data.score

    await session.commit()
    await session.refresh(current_user)

    return {"score": current_user.score}


@router.get("/get-score/")
async def get_score(current_user: User = Depends(get_current_user)):
    return {"score": current_user.score}


@router.post("/continue-game/{cost}")
async def continue_game(cost: int,
                        current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    
    if current_user.gold < cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка. Денег нема."
        )
    
    current_user.gold -= cost

    await session.commit()
    await session.refresh(current_user)

    return {
        "status": "success",
        "message": "Успешно снято золото. Продолжаем играть.",
        "gold": current_user.gold,
        "score": current_user.score,
        "diamond": current_user.diamond
    }
    
    






    


