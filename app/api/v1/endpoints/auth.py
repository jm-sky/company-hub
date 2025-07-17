from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LoginResponseData,
    RegisterRequest,
    RegisterResponse,
    RegisterResponseData,
    UserResponse,
    UserProfileResponse,
)
from app.deps import get_db, get_current_active_user
from app.crud.users import authenticate_user, create_user, get_user_by_email
from app.utils.security import create_access_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user

    - **email**: User email
    - **password**: User password
    """

    # Authenticate user
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    user_response = UserResponse(
        id=user.id, # type: ignore
        email=user.email, # type: ignore
        name=user.name, # type: ignore
        plan=user.plan, # type: ignore
        created_at=user.created_at, # type: ignore
        is_active=user.is_active # type: ignore
    )

    return LoginResponse(
        data=LoginResponseData(token=access_token, user=user_response),
        success=True
    )


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register new user

    - **email**: User email
    - **password**: User password
    - **name**: User name (optional)
    """

    # Check if user already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    try:
        user = create_user(db, request.email, request.password, request.name, plan="free")
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    user_response = UserResponse(
        id=user.id, # type: ignore
        email=user.email, # type: ignore
        name=user.name, # type: ignore
        plan=user.plan, # type: ignore
        created_at=user.created_at, # type: ignore
        is_active=user.is_active # type: ignore
    )

    return RegisterResponse(
        data=RegisterResponseData(token=access_token, user=user_response),
        success=True
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_info(current_user=Depends(get_current_active_user)):
    """Get current user information."""
    user_data = UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        plan=current_user.plan,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )
    
    return UserProfileResponse(
        data=user_data,
        success=True
    )
