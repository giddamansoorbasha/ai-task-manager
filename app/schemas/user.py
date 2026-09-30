from pydantic import BaseModel, EmailStr

class SignUp(BaseModel):
    name: str
    email: EmailStr
    password: str

class SignIn(BaseModel):
    email: EmailStr
    password: str

class SignUpResponse(BaseModel):
    user_id: int
    name: str
    email: str