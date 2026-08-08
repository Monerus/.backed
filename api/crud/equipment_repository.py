from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from api.crud.auth_utils import *
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(prefix="/weapon", tags=["Weapon"])

@router.post("/upgrade/{item_type}")
async def upgrade_equipment(
    item_type: str,
    # current_user: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    # 1. Ищем предмет пользователя по его типу
    result = await session.execute(
        select(Equipment).where(
            Equipment.user_id == current_user.id,
            # Equipment.user_id == current_user, 
            Equipment.item_type == item_type
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    # 2. Проверяем баланс золота
    if current_user.gold < item.improvement:
        raise HTTPException(status_code=400, detail="Недостаточно золота")

    # 3. Списываем золото
    current_user.gold -= item.improvement

    # 4. Прокачиваем уровень и стоимость
    item.level += 1
    item.improvement = int(item.improvement * 1.5)

    # 5. Динамически обновляем статы в зависимости от типа предмета
    if item_type == "weapon":
        # У кирки увеличиваем урон
        item.stats["damage"] = item.stats.get("damage", 1) + 1
    elif item_type == "helmet":
        # У шлема увеличиваем защиту (пример)
        item.stats["health"] = item.stats.get("health", 1) + 2
    elif item_type == "suit":
        # У костюма увеличиваем кислород/запас (пример)
        item.stats["health"] = item.stats.get("oxygen", 100) + 20

    # ОБЯЗАТЕЛЬНО для SQLAlchemy: говорим, что JSON-поле было изменено
    flag_modified(item, "stats")

    session.add(item)
    session.add(current_user)

    try:
        await session.commit()
        await session.refresh(item)
        await session.refresh(current_user)
        
        return {
            "message": f"Предмет {item_type} успешно улучшен!",
            "level": item.level,
            "next_cost": item.improvement,
            "remaining_gold": current_user.gold,
            "stats": item.stats
        }
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка покупки: {e}"
        )

@router.get("/equipment/{item_type}")
async def get_equipment(item_type: str,
                        current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):

    result = await session.execute(
            select(Equipment).where(
                Equipment.user_id == current_user.id,
                Equipment.item_type == item_type
            )
        )
    item = result.scalar_one_or_none()

    return item