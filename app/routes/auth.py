import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.database import get_async_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import SignUp, SignUpResponse

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@auth_router.post("/signup", response_model=SignUpResponse)
async def sign_up(user: SignUp, db: AsyncSession = Depends(get_async_db)):
    logger.info("Signup attempt")

    if await get_user_by_email(db, user.email):
        logger.warning("Signup rejected: email already registered")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = await run_in_threadpool(hash_password, user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed)

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        logger.warning("Signup rejected: duplicate email (race)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    except Exception:
        await db.rollback()
        logger.exception("Signup failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")

    logger.info("Signup successful user_id=%s", new_user.user_id)
    return new_user


@auth_router.post("/login")
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    logger.info("Login attempt")

    user = await get_user_by_email(db, form_data.username.lower())
    valid = user is not None and await run_in_threadpool(
        verify_password, form_data.password, user.hashed_password
    )
    if not valid:
        logger.warning("Login failed: invalid credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    access_token = create_access_token({"email": user.email, "role": user.role})

    logger.info("Login successful user_id=%s", user.user_id)
    return {"access_token": access_token, "token_type": "bearer"}