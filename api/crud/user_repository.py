from api.models import *
from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import BackgroundTasks ,Depends, status, HTTPException, APIRouter
from api.crud.auth_utils import *
from datetime import datetime, timezone
from sending_letters import *
from uuid import UUID
router = APIRouter(prefix='/auth', tags=["User"])


@router.post('/login/', response_model=UserResponse)
async def create_code(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    stmt = select(User).where(User.email == user_in.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    new_code = generate_random_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)

    if user:
        user.code = new_code
        user.code_expires_at = expires_at
    else:
        user = User(            
            email=user_in.email,
            code=new_code,
            code_expires_at=expires_at
        )
        session.add(user)

    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании/обновлении пользователя: {e}"
        )

    result_equipment = await session.execute(
        select(Equipment).where(Equipment.user_id == user.id)
    )
    existing_equipment = result_equipment.scalars().all()

    if not existing_equipment:
        starter_items = [
            Equipment(user_id=user.id, item_type="weapon", level=1, improvement=10, stats={"damage": 1}),
            Equipment(user_id=user.id, item_type="helmet", level=1, improvement=25, stats={"health": 50}),
            Equipment(user_id=user.id, item_type="suit", level=1, improvement=25, stats={"health": 50}),
        ]
        session.add_all(starter_items)

    background_tasks.add_task(send_email_code, user.email, user.code)

    try:
        await session.commit()
        await session.refresh(user)
        return user
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении данных {e}"
        )

@router.post('/verify/')
async def login(
    user_in: UserBase,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    stmt = select(User).where(User.email == user_in.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.code != user_in.code:
        raise HTTPException(status_code=400, detail="Неверный email или код")
    
    if user.code_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Код истек")
    
    try:
    # 4. Генерация токенов
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
    except  Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh")
async def refresh_token(
    body: RefreshTokenSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user_id_str = verify_refresh_token(body.refresh_token)

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат идентификатора пользователя в токене"
        )
    
    # 3. Ищем пользователя в базе данных через session.get
    user = await session.get(User, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    new_access_token = create_access_token(user)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

# Получение всех пользователей
@router.get("/users/", response_model=None)
async def get_users(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    result = await session.execute(select(User))
    stmt = result.scalars().all()
    return stmt


# Получение данных пользователя.
@router.get("/me/", response_model=None)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
