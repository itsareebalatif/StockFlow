from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
