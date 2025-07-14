from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseProvider(ABC):
    """Base class for all external data providers."""

    def __init__(self, name: str):
        self.name = name
        self.last_request_time: Optional[datetime] = None

    @abstractmethod
    async def fetch_data(self, identifier: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from external provider.

        Args:
            identifier: Company identifier (NIP, REGON, etc.)
            **kwargs: Additional parameters

        Returns:
            Dict containing the fetched data

        Raises:
            ProviderError: If the request fails
        """
        pass

    @abstractmethod
    def validate_identifier(self, identifier: str) -> bool:
        """
        Validate if the identifier is valid for this provider.

        Args:
            identifier: The identifier to validate

        Returns:
            bool: True if valid, False otherwise
        """
        pass

    @abstractmethod
    def is_rate_limited(self) -> bool:
        """
        Check if this provider is currently rate limited.

        Returns:
            bool: True if rate limited, False otherwise
        """
        pass

    @abstractmethod
    def get_next_available_time(self) -> Optional[datetime]:
        """
        Get the next time this provider will be available.

        Returns:
            datetime: Next available time or None if not rate limited
        """
        pass


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, provider: str, status_code: Optional[int] = None):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(self.message)


class RateLimitError(ProviderError):
    """Exception raised when provider rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: Optional[datetime] = None):
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {provider}"
        if retry_after:
            message += f". Retry after {retry_after}"
        super().__init__(message, provider, 429)


class ValidationError(ProviderError):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, provider: str):
        super().__init__(message, provider, 400)
