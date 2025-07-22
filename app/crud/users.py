"""CRUD operations for users."""

from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User
from app.utils.security import hash_password, verify_password
from app.security.oauth import OAuthUserInfo


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str, name: Optional[str] = None, plan: str = "free") -> User:
    """Create a new user."""
    hashed_password = hash_password(password)
    user = User(
        email=email,
        name=name,
        password_hash=hashed_password,
        plan=plan,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not user.password_hash:  # OAuth user without password
        return None
    if not verify_password(password, user.password_hash): # type: ignore
        return None
    if not user.is_active: # type: ignore
        return None
    return user


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user fields."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for field, value in kwargs.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def get_user_by_github_id(db: Session, github_id: str) -> Optional[User]:
    """Get user by GitHub ID."""
    return db.query(User).filter(User.github_id == github_id).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID."""
    return db.query(User).filter(User.google_id == google_id).first()


def create_oauth_user(db: Session, oauth_info: OAuthUserInfo, access_token: str, refresh_token: Optional[str] = None) -> User:
    """Create a new user from OAuth information."""
    # Check if user already exists by email
    existing_user = get_user_by_email(db, oauth_info.email)
    if existing_user:
        # Update existing user with OAuth info
        if oauth_info.provider == "github":
            existing_user.github_id = oauth_info.provider_id
            existing_user.github_username = oauth_info.username
        elif oauth_info.provider == "google":
            existing_user.google_id = oauth_info.provider_id
            existing_user.google_email = oauth_info.email
        
        existing_user.oauth_provider = oauth_info.provider
        existing_user.oauth_access_token = access_token
        existing_user.oauth_refresh_token = refresh_token
        existing_user.avatar_url = oauth_info.avatar_url
        if oauth_info.name and not existing_user.name:
            existing_user.name = oauth_info.name
        
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Create new OAuth user
    user_data = {
        "email": oauth_info.email,
        "name": oauth_info.name,
        "password_hash": None,  # No password for OAuth users
        "plan": "free",
        "is_active": True,
        "oauth_provider": oauth_info.provider,
        "oauth_access_token": access_token,
        "oauth_refresh_token": refresh_token,
        "avatar_url": oauth_info.avatar_url,
    }
    
    if oauth_info.provider == "github":
        user_data["github_id"] = oauth_info.provider_id
        user_data["github_username"] = oauth_info.username
    elif oauth_info.provider == "google":
        user_data["google_id"] = oauth_info.provider_id
        user_data["google_email"] = oauth_info.email
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_oauth_user(db: Session, provider: str, provider_id: str) -> Optional[User]:
    """Get user by OAuth provider and provider ID."""
    if provider == "github":
        return get_user_by_github_id(db, provider_id)
    elif provider == "google":
        return get_user_by_google_id(db, provider_id)
    return None
