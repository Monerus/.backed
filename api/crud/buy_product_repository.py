from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import *
from api.crud.auth_utils import *

router = APIRouter(prefix='/product', tags=["Buy-Product"])


# Покупка товара идет через spriteIndex
@router.post("/buy/{category_id}/{sprite_index}/")
async def buy_product(
    category_id: int,
    sprite_index: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Product).where(
            Product.category_id == category_id,
            Product.spriteIndex == sprite_index
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    already_bought = await session.execute(
        select(UserProduct.id).where(
            UserProduct.user_id == current_user.id,
            UserProduct.product_id == product.id
        )
    )

    if already_bought.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Товар уже куплен")

    if current_user.gold < product.price:
        raise HTTPException(status_code=400, detail="Недостаточно золота")

    current_user.gold -= product.price

    session.add(
        UserProduct(
            user_id=current_user.id,
            product_id=product.id
        )
    )

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка покупки: {e}"
        )

    return {
        "status": "success",
        "bought_product": product.id,
        "price": product.price,
        "remaining_gold": current_user.gold
    }

# Показывать, какие товары у него есть.
@router.get("/inventory/{category_id}/")
async def get_inventory(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    result = await session.execute(
        select(Product)
        .join(UserProduct, Product.id == UserProduct.product_id)
        .where(
            UserProduct.user_id == current_user.id,
            Product.category_id == category_id
        )
        .order_by(Product.spriteIndex)
        .distinct()
    )
    return result.scalars().all()