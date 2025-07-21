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
    OAuthCallbackRequest,
    OAuthCallbackResponse,
    OAuthAuthUrlRequest,
    OAuthAuthUrlResponse,
)
from app.deps import get_db, get_current_active_user
from app.crud.users import authenticate_user, create_user, get_user_by_email, create_oauth_user, get_oauth_user
from app.utils.security import create_access_token
from app.security.oauth import oauth_service

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
        is_active=user.is_active, # type: ignore
        oauth_provider=user.oauth_provider, # type: ignore
        github_username=user.github_username, # type: ignore
        google_email=user.google_email, # type: ignore
        avatar_url=user.avatar_url # type: ignore
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
        is_active=user.is_active, # type: ignore
        oauth_provider=user.oauth_provider, # type: ignore
        github_username=user.github_username, # type: ignore
        google_email=user.google_email, # type: ignore
        avatar_url=user.avatar_url # type: ignore
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
        is_active=current_user.is_active,
        oauth_provider=current_user.oauth_provider,
        github_username=current_user.github_username,
        google_email=current_user.google_email,
        avatar_url=current_user.avatar_url
    )
    
    return UserProfileResponse(
        data=user_data,
        success=True
    )


@router.post("/oauth/auth-url", response_model=OAuthAuthUrlResponse)
async def get_oauth_auth_url(request: OAuthAuthUrlRequest):
    """
    Get OAuth authorization URL for a provider
    
    - **provider**: OAuth provider name ('github' or 'google')
    """
    try:
        state = oauth_service.generate_state()
        auth_url = oauth_service.get_authorization_url(request.provider, state)
        
        return OAuthAuthUrlResponse(
            data={"auth_url": auth_url, "state": state},
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/oauth/{provider}/callback", response_model=OAuthCallbackResponse)
async def oauth_callback(
    provider: str,
    request: OAuthCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback
    
    - **provider**: OAuth provider name ('github' or 'google')
    - **code**: Authorization code from OAuth provider
    - **state**: CSRF protection state parameter
    """
    try:
        # Complete OAuth flow and get user info
        oauth_user_info = await oauth_service.complete_oauth_flow(provider, request.code)
        
        # Check if user already exists by provider ID
        existing_user = get_oauth_user(db, provider, oauth_user_info.provider_id)
        
        if existing_user:
            # Update existing user's OAuth info
            user = existing_user
            if provider == "github":
                user.github_username = oauth_user_info.username
            elif provider == "google":
                user.google_email = oauth_user_info.email
            user.avatar_url = oauth_user_info.avatar_url
            db.commit()
            db.refresh(user)
        else:
            # Create new user or link OAuth to existing email
            token_response = await oauth_service.exchange_code_for_token(provider, request.code)
            user = create_oauth_user(
                db, 
                oauth_user_info, 
                token_response.access_token, 
                token_response.refresh_token
            )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            plan=user.plan,
            created_at=user.created_at,
            is_active=user.is_active,
            oauth_provider=user.oauth_provider,
            github_username=user.github_username,
            google_email=user.google_email,
            avatar_url=user.avatar_url
        )
        
        return OAuthCallbackResponse(
            data=LoginResponseData(token=access_token, user=user_response),
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during OAuth authentication: {str(e)}"
        )
