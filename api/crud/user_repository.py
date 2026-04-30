from api.models import *
from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, status, HTTPException, APIRouter
from api.crud.auth_utils import *


router = APIRouter(prefix='/auth', tags=["Users"])

# Регистрация
@router.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    user = Users(**user_in.model_dump())
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Почта уже занята"
        )
    return user


#Вход
@router.post("/login/", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_in: UserBase,
                session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(
        select(Users)
        .where(Users.email == user_in.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Неверные данные")
    try:
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
    except  Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )
    return Token(access_token=access_token, refresh_token=refresh_token)


# Получение всех пользователей
@router.get("/users/", response_model=None)
async def get_users(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(select(Users))
    stmt = result.scalars().all()
    return stmt


# Получение данных пользователя.
@router.get("/me/", response_model=None)
async def read_users_me(current_user: Users = Depends(get_current_user)) -> Users:
    return current_user
