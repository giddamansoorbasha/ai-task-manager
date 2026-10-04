from pydantic import BaseModel, EmailStr, Field, field_validator


class SignUp(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


class SignUpResponse(BaseModel):
    user_id: int
    name: str
    email: str