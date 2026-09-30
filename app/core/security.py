import enum
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.database import get_async_db
from app.models.user import User

user_token = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_content = CryptContext(schemes=["argon2"])

def hash_password(plain_password: str) -> str:
    return pwd_content.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_content.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_TIME)
    payload.update({"exp": expire, 
                    "sub": data.get("email"), 
                    "role": data.get("role").value if isinstance(data.get("role"), enum.Enum) else data.get("role")
                })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_TIME)
    payload.update({"exp": expire, 
                    "sub": data.get("email"),
                    "role": data.get("role").value if isinstance(data.get("role"), enum.Enum) else data.get("role")
                })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
async def get_current_user(token: str = Depends(user_token), db: AsyncSession = Depends(get_async_db)):
    payload = decode_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user