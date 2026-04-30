from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    gold: int = 100
    diamond: int = 100

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class UserScore(BaseModel):
    score: int