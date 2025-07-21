"""Main MF provider class that orchestrates all components."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import httpx

from app.providers.base import BaseProvider, ProviderError, RateLimitError, ValidationError
from app.utils.validators import validate_nip

from .http_client import MfHttpClient
from .rate_limiter import MfRateLimiter
from .data_parser import MfDataParser
from .api_client import MfApiClient

logger = logging.getLogger(__name__)


class MfProvider(BaseProvider):
    """Provider for MF (Biała Lista) - Polish VAT whitelist using refactored components."""

    def __init__(self, api_url: str = "https://wl-api.mf.gov.pl"):
        super().__init__("MF")

        # Initialize components
        self.http_client = MfHttpClient(api_url=api_url, timeout=10)
        self.rate_limiter = MfRateLimiter(requests_per_second=1.0)
        self.data_parser = MfDataParser()
        self.api_client = MfApiClient(
            http_client=self.http_client,
            data_parser=self.data_parser
        )

    def validate_identifier(self, identifier: str) -> bool:
        """Validate NIP for MF API."""
        return validate_nip(identifier)

    def is_rate_limited(self) -> bool:
        """Check if we're rate limited."""
        return self.rate_limiter.is_rate_limited()

    def get_next_available_time(self) -> Optional[datetime]:
        """Get next available time for requests."""
        return self.rate_limiter.get_next_available_time()

    async def fetch_data(self, nip: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch company data from MF API.

        Args:
            nip: Company NIP number
            **kwargs: Additional parameters (date for historical data)

        Returns:
            Dict containing MF data
        """
        if not self.validate_identifier(nip):
            logger.error(f"Invalid NIP: {nip}")
            raise ValidationError(f"Invalid NIP: {nip}", self.name)

        if self.is_rate_limited():
            logger.error(f"Rate limit exceeded for NIP: {nip}")
            raise RateLimitError(self.name, self.get_next_available_time())

        # Get date parameter (format: YYYY-MM-DD)
        date_param = kwargs.get("date")
        if not date_param:
            date_param = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            # Record request for rate limiting
            self.rate_limiter.record_request()

            # Fetch data using API client
            result = await self.api_client.search_company(nip, date_param)
            return result

        except httpx.TimeoutException:
            raise ProviderError(f"MF API timeout for NIP {nip}", self.name, 408)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitError(self.name)
            raise ProviderError(f"MF API error: {e.response.status_code}", self.name, e.response.status_code)
        except RuntimeError as e:
            if "Rate limit exceeded" in str(e):
                raise RateLimitError(self.name)
            raise ProviderError(f"MF API error: {str(e)}", self.name)
        except Exception as e:
            logger.error(f"MF API error for NIP {nip}: {str(e)}")
            raise ProviderError(f"MF API error: {str(e)}", self.name)
