from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class RefreshTokenSchema(BaseModel):
    refresh_token: str

class UserScore(BaseModel):
    score: int

class UserBase(BaseModel):
    email: EmailStr
    code: int

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    gold: int = 100
    diamond: int = 100
    code: int
    score: int