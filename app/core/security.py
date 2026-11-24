import uuid
from datetime import datetime, timedelta, timezone
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_db
from app.models.user import User

user_token = OAuth2PasswordBearer(tokenUrl="/auth/login")
pw = CryptContext(schemes=["argon2"])


def hash_password(plain_password: str) -> str:
    return pw.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pw.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    user_id = data.get("sub")
    payload = {"sub": str(user_id), "type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_TIME)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    user_id = data.get("sub")
    payload = {"sub": str(user_id), "type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_TIME)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})


async def get_current_user(token: str = Depends(user_token), db: AsyncSession = Depends(get_async_db)) -> User:
    
    payload = decode_token(token)
    try:
        user_id = uuid.UUID(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload", headers={"WWW-Authenticate": "Bearer"})

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
      
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    
    return user