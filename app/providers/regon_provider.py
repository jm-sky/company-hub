"""Refactored REGON provider using helper classes."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.providers.base import BaseProvider, ProviderError, RateLimitError, ValidationError
from app.providers.regon import (
    RegonSoapClient,
    RegonSessionManager,
    RegonRateLimiter,
    RegonDataMapper,
    RegonApiClient,
    EntityType,
)
from app.utils.validators import validate_nip
from app.config import settings

logger = logging.getLogger(__name__)


class RegonProvider(BaseProvider):
    """Refactored REGON API provider implementation."""
    
    def __init__(self):
        super().__init__("regon")
        
        # Initialize helper components
        self.soap_client = RegonSoapClient(settings.regon_api_url)
        self.session_manager = RegonSessionManager(self.soap_client, settings.regon_api_key)
        self.rate_limiter = RegonRateLimiter()
        self.data_mapper = RegonDataMapper()
        self.api_client = RegonApiClient(self.soap_client, self.session_manager, self.data_mapper)
        
    def validate_identifier(self, identifier: str) -> bool:
        """Validate NIP format."""
        return validate_nip(identifier)
        
    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        return self.rate_limiter.is_rate_limited()
        
    def get_next_available_time(self) -> Optional[datetime]:
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
            # Record the request for rate limiting
            self.rate_limiter.record_request()
            
            # Step 1: Search for company
            search_result = await self.api_client.search_company(nip)
            
            # Step 2: Build basic company info
            company_info = self.data_mapper.build_basic_company_info(nip, search_result)
            
            if not company_info["found"]:
                return company_info
                
            # Step 3: Try to get detailed report if we have REGON
            regon = company_info.get("regon")
            entity_type_str = company_info.get("entity_type")
            
            if regon and entity_type_str:
                try:
                    entity_type = self.data_mapper.map_type_to_entity(entity_type_str)
                    detailed_data = await self.api_client.get_detailed_report(regon, entity_type)
                    
                    company_info["detailed_data"] = detailed_data
                    company_info["report_type"] = detailed_data.get("report_type", "")
                    
                except Exception as e:
                    # If detailed report fails, still return basic info
                    logger.warning(f"Failed to get detailed report for {nip}: {str(e)}")
                    company_info["detailed_error"] = str(e)
                    
            return company_info
            
        except (RateLimitError, ValidationError):
            # Re-raise these specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching data for NIP {nip}: {str(e)}")
            raise ProviderError(f"Unexpected error: {str(e)}", self.name)