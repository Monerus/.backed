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
    result = await session.execute(select(Users.name, Users.score)
                                   .order_by(desc(Users.score))
                                   .limit(200))
    stmt = result.mappings().all()
    return stmt


@router.get("/me/")
async def get_my_rating(session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                        current_user: Users = Depends(get_current_user)):
    
    query_rank = select(func.count(Users.id)).where(Users.score > current_user.score)

    result = await session.execute(query_rank)

    rank = result.scalar_one() + 1
    
    return {
        "rank": rank,
        "name": current_user.name,
        "score": current_user.score
    }
    

# Считать шаги и записывать их в базу данных
@router.post('/score')
async def save_score(data: UserScore,
                     current_user: Users = Depends(get_current_user),
                     session: AsyncSession = Depends(db_helper.scoped_session_dependency)): 
    
    current_user.score += data.score

    await session.commit()
    await session.refresh(current_user)

    return {"score": current_user}


@router.get("/get-score/")
async def get_score(current_user: Users = Depends(get_current_user)):
    return {"score": current_user.score}





    


