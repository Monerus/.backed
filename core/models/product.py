from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from sqlalchemy import ForeignKey

# Товар.
class Product(Base):
    __tablename__ = "product"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str]
    price: Mapped[int]
    damage: Mapped[int] #Исправить
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    spriteIndex: Mapped[int] = mapped_column(default=0)
    spriteCategory: Mapped[str]
    spriteLabel: Mapped[str]


# Категории к товарам.
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


# Покупка товаров.
class UserProduct(Base):
    __tablename__ = "user_products"
    
    id: Mapped[int] = mapped_column(primary_key=True)  
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))