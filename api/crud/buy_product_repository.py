from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import *
from api.crud.auth_utils import *
from typing import Optional

router = APIRouter(prefix='/product', tags=["Buy-Product"])


# Покупка товара идет через spriteIndex
@router.post("/buy/{category_id}/{sprite_index}/")
async def buy_product(category_id: int,
                      sprite_index: int,
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                      current_user: Users = Depends(get_current_user)):
    
    result = await session.execute(
        select(Product).where(
            Product.category_id == category_id,
            Product.spriteIndex == sprite_index
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    existing_purchase = await session.execute(
        select(UserProduct).where(
            UserProduct.user_id == current_user.id,
            UserProduct.product_id == product.id
            )
    )

    if existing_purchase.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Товар уже куплен")
    
    

    # Проверяем деньги
    if current_user.gold < product.price:
        raise HTTPException(status_code=400, detail="Недостаточно золота")

    # Списываем золото
    current_user.gold -= product.price

    user_product = UserProduct(
        user_id=current_user.id,
        product_id=product.id
    )

    session.add(user_product)

    try:
        await session.commit()
        await session.refresh(user_product)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка: {e}")
    
    return {"message": "Покупка успешна"}


# Показывать, какие товары у него есть.
@router.get("/inventory/{category_id}/")
async def get_inventory(
    category_id: int,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    query = (
        select(Product)
        .join(UserProduct, Product.id == UserProduct.product_id)
        .where(UserProduct.user_id == current_user.id)
    )

    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    query = query.order_by(Product.spriteIndex)

    result = await session.execute(query)
    products = result.scalars().all()
    
    return products