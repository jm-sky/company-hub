"""Main REGON provider class that orchestrates all components."""

import logging
from datetime import datetime
from typing import Dict, Any
from app.providers.base import (
    BaseProvider,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from app.utils.validators import validate_nip
from app.config import settings

from .soap_client import RegonSoapClient
from .session_manager import RegonSessionManager
from .rate_limiter import RegonRateLimiter
from .data_mapper import RegonDataMapper
from .api_client import RegonApiClient

logger = logging.getLogger(__name__)


class RegonProvider(BaseProvider):
    """REGON API provider implementation using refactored components."""

    def __init__(self):
        super().__init__("regon")

        # Initialize components
        self.soap_client = RegonSoapClient(
            api_url=settings.regon_api_url,
            timeout=30
        )
        self.session_manager = RegonSessionManager(
            soap_client=self.soap_client,
            api_key=settings.regon_api_key
        )
        self.rate_limiter = RegonRateLimiter()
        self.data_mapper = RegonDataMapper()
        self.api_client = RegonApiClient(
            soap_client=self.soap_client,
            session_manager=self.session_manager,
            data_mapper=self.data_mapper
        )

    def validate_identifier(self, identifier: str) -> bool:
        """Validate NIP format."""
        return validate_nip(identifier)

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        return self.rate_limiter.is_rate_limited()

    def get_next_available_time(self) -> datetime:
        """Get next available time for requests."""
        return self.rate_limiter.get_next_available_time()

    async def fetch_data(self, nip: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch company data from REGON API.

        This is a two-step process:
        1. Search by NIP to get basic info and determine entity type
        2. Get detailed report based on entity type
        """
        logger.info(f"Fetching data for NIP: {nip}")

        if not self.validate_identifier(nip):
            logger.error(f"Invalid NIP format: {nip}")
            raise ValidationError(f"Invalid NIP format: {nip}", self.name)

        if self.is_rate_limited():
            logger.warning(f"Rate limited for NIP: {nip}")
            raise RateLimitError(self.name, self.get_next_available_time())

        try:
            # Record request for rate limiting
            self.rate_limiter.record_request()

            # Step 1: Search for company
            search_result = await self.api_client.search_company(nip)

            if not search_result["found"]:
                return {
                    "found": False,
                    "nip": nip,
                    "message": search_result.get("message", "Company not found in REGON database"),
                    "fetched_at": datetime.now().isoformat(),
                }

            # Step 2: Build basic company info
            basic_info = self.data_mapper.build_basic_company_info(nip, search_result)

            if not basic_info["found"]:
                return basic_info

            # Step 3: Try to get detailed report if we have REGON
            regon = basic_info.get("regon")
            if regon:
                try:
                    entity_type = self.data_mapper.map_type_to_entity(
                        search_result["data"].get("Typ", "")
                    )
                    detailed_data = await self.api_client.get_detailed_report(regon, entity_type)
                    basic_info["detailed_data"] = detailed_data
                    basic_info["report_type"] = detailed_data.get("report_type", "")
                except Exception as e:
                    # If detailed report fails, still return basic info
                    logger.warning(f"Failed to get detailed report for {regon}: {str(e)}")
                    basic_info["detailed_error"] = str(e)

            return basic_info

        except (ValidationError, RateLimitError):
            # Re-raise these specific errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching data for NIP {nip}: {str(e)}")
            raise ProviderError(f"Unexpected error: {str(e)}", self.name)
