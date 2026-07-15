from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional
import bcrypt
import jwt
from cryptography.fernet import Fernet
from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.PyJWTError:
        return None


@lru_cache(maxsize=1)
def _get_oauth_token_fernet() -> Fernet:
    if not settings.oauth_token_encryption_key:
        raise RuntimeError(
            "OAUTH_TOKEN_ENCRYPTION_KEY is not configured. "
            "Generate one with `python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"`."
        )
    return Fernet(settings.oauth_token_encryption_key.encode())


def encrypt_oauth_token(token: Optional[str]) -> Optional[str]:
    """Encrypt an OAuth access/refresh token before persisting it."""
    if token is None:
        return None
    return _get_oauth_token_fernet().encrypt(token.encode('utf-8')).decode('utf-8')


def decrypt_oauth_token(token: Optional[str]) -> Optional[str]:
    """Decrypt a previously-encrypted OAuth access/refresh token."""
    if token is None:
        return None
    return _get_oauth_token_fernet().decrypt(token.encode('utf-8')).decode('utf-8')
