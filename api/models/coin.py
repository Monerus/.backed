from pydantic import BaseModel, ConfigDict
from datetime import datetime
from core.models import *

class CoinBase(BaseModel):
    gold: int | None = None
    diamond: int | None = None
    level: int

class CoinResponse(CoinBase):
    id: int
    gold: int
    diamond: int
    level: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserCoinBase(BaseModel):
    id: int
    coin_id: int

    is_opened: bool
    model_config = ConfigDict(from_attributes=True)