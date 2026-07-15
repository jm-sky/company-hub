"""Helpers for setting/clearing the httpOnly session cookie."""

from fastapi import Response

from app.config import settings

ACCESS_TOKEN_COOKIE_NAME = "access_token"


def set_access_token_cookie(response: Response, token: str) -> None:
    """Set the JWT session cookie. httpOnly so it's inaccessible to JS (XSS mitigation)."""
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",
    )


def clear_access_token_cookie(response: Response) -> None:
    """Clear the JWT session cookie (logout)."""
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",
    )
