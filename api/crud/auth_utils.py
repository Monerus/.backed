from datetime import timedelta, datetime
import jwt
from sqlalchemy import select
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import *
from typing import Annotated
from api.models import *
import secrets


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")

def encode_jwt(payload: dict, 
               private_key: str = settings.JWT_SECRET,
               algorithms: str = settings.JWT_ALGORITHM,
               exripe_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
               expire_timedelta: timedelta | None = None
               ) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=exripe_minutes)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, private_key, algorithm=algorithms)



def decode_jwt(token: str | bytes, 
               public_key: str = settings.JWT_SECRET, 
               algorithms: str = settings.JWT_ALGORITHM):
    return jwt.decode(token, public_key, algorithms)


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {"type": token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        exripe_minutes=expire_minutes,
        expire_timedelta=expire_timedelta)


#create access token
def create_access_token(user) -> str:
    jwt_payload = {
        "id": str(user.id),
        "email": user.email
    }
    return create_jwt(
        token_type="access",
        token_data=jwt_payload,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

def generate_random_code():
    return secrets.randbits(20)

#create refresh token
# def create_refresh_token(user) -> str:
#     jwt_payload = {
#         "sub": str(user.id),
#         "email": user.emil,
#         "type": "refresh"
#     }
#     return create_jwt(
#         token_type="refresh",
#         token_data=jwt_payload,
#         expire_timedelta=timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS),
#         secret_key=settings.JWT_SECRET
#     )

def create_refresh_token(user) -> str:
    jwt_payload = {
        "id": str(user.id),       
        "email": user.email,     
        "type": "refresh"
    }
    return create_jwt(
        token_type="refresh",
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], 
                           session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка с пользователем",
        headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ошибка с пользователем")
        return user
    except:
        raise credentials_exception


def verify_refresh_token(refresh_token: str) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен (используем decode_jwt, чтобы задействовать настройки по умолчанию)
        payload = decode_jwt(refresh_token)
        
        # Проверяем тип токена
        if payload.get("type") != "refresh":
            raise credentials_exception
            
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
            
        return user_id # Возвращаем int, чтобы поиск в базе пошел корректно
    except jwt.PyJWTError:
        raise credentials_exception