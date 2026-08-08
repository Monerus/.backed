from core.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from fastapi import Depends, status, HTTPException, APIRouter
from api.models import * 
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


@router.get("/ss")
async def get_prod(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    res = await session.execute(select(Product))
    result = res.scalars().all()
    return result


#Показывать товар по сортировке по категориям
@router.get("/", response_model=list[ProductResponse])
async def get_products(
    category_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(
    select(Product)
    .where(Product.category_id == category_id)
    .where(
        ~exists().where(
            (UserProduct.user_id == current_user.id) &
            (UserProduct.product_id == Product.id)
        )
    )
    .order_by(Product.spriteIndex)
    .limit(4)
)
    return result.scalars().all()