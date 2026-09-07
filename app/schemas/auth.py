
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.enums import UserRole

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str ="bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token:str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool
