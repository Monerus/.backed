from pydantic import BaseModel, ConfigDict


# Карты
class CardsBase(BaseModel):
    image_url: str
    text: str
    title: str
    set_id: int

class CardsCreate(CardsBase):
    pass

class CardsResponse(CardsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Комплект карточек

class SetCardsBase(BaseModel):
    name: str
    level: int

class SetCardsCreate(SetCardsBase):
    pass

class SetCardsResponse(SetCardsBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
