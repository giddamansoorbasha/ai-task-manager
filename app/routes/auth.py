import logging
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import hash_password, verify_password, create_access_token
from app.core.database import get_async_db
from app.models.user import User
from app.schemas.user import SignUp, SignUpResponse

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/signup", response_model=SignUpResponse)
async def sign_up(user: SignUp, db: AsyncSession = Depends(get_async_db)):
    
    logger.info("User signup attempt")
    
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    new_user = User(name=user.name, email=user.email, hashed_password=hash_password(user.password))
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Could not create user")

    logger.info("User signup successful")
    
    return new_user


@auth_router.post("/login")
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):

    logger.info("User login attempt")

    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    access_token = create_access_token({"email": user.email, "role":user.role})

    logger.info("User login successful")
    
    return {"access_token": access_token, "token_type": "bearer"}