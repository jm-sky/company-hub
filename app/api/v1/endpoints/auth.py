from fastapi import APIRouter
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LoginResponseData,
    RegisterRequest,
    RegisterResponse,
    RegisterResponseData,
    UserResponse,
)
from datetime import datetime

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user

    - **email**: User email
    - **password**: User password
    """

    # Mock user response - replace with actual authentication logic
    mock_user = UserResponse(
        id=1,
        email=request.email,
        plan="free",
        created_at=datetime.now(),
        is_active=True
    )

    return LoginResponse(data=LoginResponseData(token="mock_jwt_token_123", user=mock_user), success=True)


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Register new user

    - **email**: User email
    - **password**: User password
    - **name**: User name (optional)
    """

    # Mock user response - replace with actual registration logic
    mock_user = UserResponse(
        id=2,
        email=request.email,
        plan="free",
        created_at=datetime.now(),
        is_active=True
    )

    return RegisterResponse(data=RegisterResponseData(token="mock_jwt_token_456", user=mock_user), success=True)
