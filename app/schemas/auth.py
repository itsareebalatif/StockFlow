
import uuid
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole

class UserRgistration(BaseModel):
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

class UserResponse(BaseModel):
    id:uuid.UUID
    email:EmailStr
    role:UserRole
    is_active: bool

    class config:
        from_attributes=True   
                     
