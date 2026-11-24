from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_async_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import SignUp, SignUpResponse, LogIn
from app.services.user import select_users, insert_user, update_user, delete_user, get_user_by_email

auth_router = APIRouter(prefix="/user", tags=["Auth"])


@auth_router.post("/signup", response_model=SignUpResponse)
async def sign_up(user: SignUp, db: AsyncSession = Depends(get_async_db)):
    hashed = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed)
    return await insert_user(db, new_user)
    

@auth_router.post("/login")
async def sign_in(user: LogIn, db: AsyncSession = Depends(get_async_db)):

    user_exist = await get_user_by_email(db, user.email)
    valid = user_exist is not None and verify_password(user.password, user_exist.hashed_password)
    
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    access_token = create_access_token({"email": user_exist.user_id})
    refresh_token = create_refresh_token({"user_id": user_exist.user_id})

    return {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}