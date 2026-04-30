from pydantic import BaseModel, ConfigDict

# Модель товаров.
class ProductBase(BaseModel):
    image_url: str
    price: int
    damage: int
    category_id: int
    spriteIndex: int

class ProductCreate(ProductBase):
    pass 

class ProductResponse(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Категории товаров.
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Покупка товаров.
class BuyProductBase(BaseModel):
    user_id: int
    product_id: int

class BuyProductBaseCreate(BuyProductBase):
    pass

class BuyProductBaseResponse(BuyProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


