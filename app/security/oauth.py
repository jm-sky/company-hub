import secrets
import httpx
from typing import Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel
from app.config import settings

class OAuthUserInfo(BaseModel):
    """Standardized OAuth user info"""
    provider: str
    provider_id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    username: Optional[str] = None

class OAuthTokenResponse(BaseModel):
    """OAuth token exchange response"""
    access_token: str
    token_type: str
    scope: Optional[str] = None
    refresh_token: Optional[str] = None

class OAuthProvider(ABC):
    """Abstract base class for OAuth providers"""

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information using access token"""
        pass

class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth provider implementation"""

    def __init__(self):
        self.client_id = settings.github_client_id
        self.client_secret = settings.github_client_secret
        self.redirect_uri = settings.github_redirect_uri
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_api_url = "https://api.github.com/user"

    def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",
            "state": state,
            "response_type": "code"
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """Exchange GitHub authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(f"GitHub OAuth error: {data.get('error_description', data['error'])}")

            return OAuthTokenResponse(
                access_token=data["access_token"],
                token_type=data.get("token_type", "bearer"),
                scope=data.get("scope"),
                refresh_token=data.get("refresh_token")
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get GitHub user information"""
        async with httpx.AsyncClient() as client:
            # Get user profile
            response = await client.get(
                self.user_api_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0
            )
            response.raise_for_status()
            user_data = response.json()

            # Get user emails
            email_response = await client.get(
                f"{self.user_api_url}/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0
            )
            email_response.raise_for_status()
            emails = email_response.json()

            # Find primary email
            primary_email = None
            for email in emails:
                if email.get("primary", False) and email.get("verified", False):
                    primary_email = email["email"]
                    break

            if not primary_email and emails:
                # Fallback to first verified email
                for email in emails:
                    if email.get("verified", False):
                        primary_email = email["email"]
                        break

            if not primary_email:
                raise ValueError("No verified email found in GitHub account")

            return OAuthUserInfo(
                provider="github",
                provider_id=str(user_data["id"]),
                email=primary_email,
                name=user_data.get("name"),
                avatar_url=user_data.get("avatar_url"),
                username=user_data.get("login")
            )

class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth provider implementation"""

    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_api_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email profile",
            "state": state,
            "response_type": "code",
            "access_type": "offline",  # For refresh tokens
            "prompt": "consent"  # Always show consent screen
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """Exchange Google authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(f"Google OAuth error: {data.get('error_description', data['error'])}")

            return OAuthTokenResponse(
                access_token=data["access_token"],
                token_type=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
                refresh_token=data.get("refresh_token")
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get Google user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_api_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                timeout=10.0
            )
            response.raise_for_status()
            user_data = response.json()

            if not user_data.get("verified_email", False):
                raise ValueError("Google account email is not verified")

            return OAuthUserInfo(
                provider="google",
                provider_id=str(user_data["id"]),
                email=user_data["email"],
                name=user_data.get("name"),
                avatar_url=user_data.get("picture"),
                username=None  # Google doesn't have usernames
            )

class OAuthService:
    """Central OAuth service for managing multiple providers"""

    def __init__(self):
        self.providers = {
            "github": GitHubOAuthProvider(),
            "google": GoogleOAuthProvider(),
        }

    def get_provider(self, provider_name: str) -> OAuthProvider:
        """Get OAuth provider by name"""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider_name}")
        return self.providers[provider_name]

    def generate_state(self) -> str:
        """Generate a secure state parameter for CSRF protection"""
        return secrets.token_urlsafe(32)

    def get_authorization_url(self, provider_name: str, state: str) -> str:
        """Generate authorization URL for provider"""
        provider = self.get_provider(provider_name)
        return provider.get_authorization_url(state)

    async def exchange_code_for_token(self, provider_name: str, code: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token"""
        provider = self.get_provider(provider_name)
        return await provider.exchange_code_for_token(code)

    async def get_user_info(self, provider_name: str, access_token: str) -> OAuthUserInfo:
        """Get user information from provider"""
        provider = self.get_provider(provider_name)
        return await provider.get_user_info(access_token)

    async def complete_oauth_flow(self, provider_name: str, code: str) -> tuple[OAuthUserInfo, OAuthTokenResponse]:
        """Complete OAuth flow: exchange code for token and get user info"""
        token_response = await self.exchange_code_for_token(provider_name, code)
        user_info = await self.get_user_info(provider_name, token_response.access_token)
        return user_info, token_response


# Global OAuth service instance
oauth_service = OAuthService()
