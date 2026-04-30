from pydantic import BaseModel, ConfigDict

class CardExchangeBase(BaseModel):
    recipient_id: int
    sender_card_id: int
    recipient_card_id: int

class CardExchangeCreate(CardExchangeBase):
    pass

class CardExchangeResponse(CardExchangeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_id: int
