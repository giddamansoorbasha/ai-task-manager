import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def select_users(db: AsyncSession):
    results = await db.execute(select(User))
    return results.scalars().all()

async def insert_user(db: AsyncSession, user: User):
    user_exist = await get_user_by_email(db, user.email)
    if user_exist:
        raise HTTPException(detail="Email already registered", status_code=status.HTTP_400_BAD_REQUEST)
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")

async def update_user(db: AsyncSession, user_id: uuid.UUID, new_name: str):
    user_exist = await db.get(User, user_id)
    if not user_exist:
        raise HTTPException(detail="user not found", status_code=status.HTTP_400_BAD_REQUEST)
    user_exist.name = new_name
    await db.commit()
    return user_exist

async def delete_user(db: AsyncSession, user_id: uuid.UUID):
    user_exist = await db.get(User, user_id)
    if not user_exist:
        raise HTTPException(detail="user not found", status_code=status.HTTP_400_BAD_REQUEST)
    query = delete(User).where(User.user_id == user_id)
    await db.execute(query)
    await db.commit()