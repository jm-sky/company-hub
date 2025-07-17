"""CRUD operations for users."""

from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User
from app.utils.security import hash_password, verify_password


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
