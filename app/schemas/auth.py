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
    name: Optional[str] = None
    plan: str
    created_at: datetime
    is_active: bool
    oauth_provider: Optional[str] = None
    github_username: Optional[str] = None
    google_email: Optional[str] = None
    avatar_url: Optional[str] = None

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

class UserProfileResponse(ApiResponse):
    data: UserResponse

# OAuth-specific schemas
class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

class OAuthCallbackResponse(ApiResponse):
    data: LoginResponseData

class OAuthAuthUrlRequest(BaseModel):
    provider: str  # 'github' or 'google'

class OAuthAuthUrlResponse(ApiResponse):
    data: dict  # {"auth_url": "...", "state": "..."}
