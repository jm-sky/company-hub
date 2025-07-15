from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.base import ApiResponse

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    plan: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class LoginResponseData(BaseModel):
    token: str
    user: UserResponse

class LoginResponse(ApiResponse):
    data: LoginResponseData

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class RegisterResponseData(BaseModel):
    token: str
    user: UserResponse

class RegisterResponse(ApiResponse):
    data: RegisterResponseData
