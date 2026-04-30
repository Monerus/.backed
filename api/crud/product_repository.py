from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, not_
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
from typing import List
from api.crud.auth_utils import *

router = APIRouter(prefix='/product', tags=["Product"])


#Создаем категории(для админа)
@router.post("/categories/", response_model=CategoryResponse)
async def create_categories(categories_in: CategoryCreate, 
                         session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    categories = Category(**categories_in.model_dump())
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



# Создаем товар(для админа)
@router.post("/categories/product/", response_model=ProductResponse)
async def create_product(product_in: ProductCreate, 
                         session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    product = Product(**product_in.model_dump())
    try:
        session.add(product)
        await session.commit()
        await session.refresh(product)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка: {e}")
    return product


#Показывать товар по сортировке по категориям
@router.get("/", response_model=None)
async def get_products(
    category_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: Users = Depends(get_current_user)
):
    # 1. Получаем ID всех товаров, которые этот пользователь уже купил
    purchased_query = await session.execute(
        select(UserProduct.product_id).where(UserProduct.user_id == current_user.id)
    )
    purchased_ids = purchased_query.scalars().all()

    # 2. Получаем товары, которых НЕТ в списке купленных
    result = await session.execute(
        select(Product)
        .where(Product.category_id == category_id)
        .where(not_(Product.id.in_(purchased_ids))) # Исключаем купленные
        .order_by(Product.spriteIndex)
        .limit(3)
    )
    
    return result.scalars().all()