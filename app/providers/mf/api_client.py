"""MF API client for high-level operations."""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
from .http_client import MfHttpClient
from .data_parser import MfDataParser

logger = logging.getLogger(__name__)


class MfApiClient:
    """Client for MF API operations."""

    def __init__(self, http_client: MfHttpClient, data_parser: MfDataParser):
        self.http_client = http_client
        self.data_parser = data_parser

    async def search_company(self, nip: str, date: str = None) -> Dict[str, Any]:
        """Search for company by NIP in MF whitelist."""
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            response = await self.http_client.search_by_nip(nip, date)

            if not response["found"]:
                if response.get("status_code") == 404:
                    return {
                        "found": False,
                        "nip": nip,
                        "date": date,
                        "message": "Company not found in MF whitelist",
                        "fetched_at": datetime.now(timezone.utc).isoformat()
                    }
                elif response.get("status_code") == 429:
                    # Let the rate limiter handle this
                    raise RuntimeError("Rate limit exceeded")
                else:
                    return {
                        "found": False,
                        "nip": nip,
                        "date": date,
                        "message": response.get("message", "Unknown error from MF API"),
                        "fetched_at": datetime.now(timezone.utc).isoformat()
                    }

            # Parse successful response
            return self.data_parser.parse_response(response["data"], nip, date)

        except Exception as e:
            logger.error(f"MF API client error for NIP {nip}: {str(e)}")
            raise
