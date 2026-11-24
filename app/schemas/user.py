from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID

class SignUp(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()

class SignUpResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    email: str

class LogIn(BaseModel):
    email: EmailStr
    password: str