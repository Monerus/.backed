from pydantic import BaseModel, ConfigDict

class WeaponBase(BaseModel):
    level: int
    damage: int
    improvement: int

class WeaponCreate(WeaponBase):
    pass

class WeaponResponse(WeaponBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

