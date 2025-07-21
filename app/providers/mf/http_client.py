"""HTTP client for MF API operations."""

import logging
from typing import Dict, Any
import httpx

logger = logging.getLogger(__name__)


class MfHttpClient:
    """HTTP client for MF API requests."""

    def __init__(self, api_url: str = "https://wl-api.mf.gov.pl", timeout: int = 10):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    async def search_by_nip(self, nip: str, date: str) -> Dict[str, Any]:
        """Search company by NIP in MF whitelist."""
        # Clean NIP (remove dashes)
        clean_nip = nip.replace("-", "")

        url = f"{self.api_url}/api/search/nip/{clean_nip}"
        params = {"date": date}

        logger.debug(f"Making MF API request to {url} with params {params}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)

            logger.debug(f"MF API response: {response.status_code}")
            logger.debug(f"MF API response content: {response.text[:500]}...")

            if response.status_code == 404:
                return {
                    "found": False,
                    "status_code": 404,
                    "message": "Company not found in MF whitelist"
                }

            if response.status_code == 429:
                return {
                    "found": False,
                    "status_code": 429,
                    "message": "Rate limit exceeded"
                }

            response.raise_for_status()

            try:
                data = response.json()
                return {
                    "found": True,
                    "status_code": 200,
                    "data": data
                }
            except Exception as e:
                logger.error(f"Failed to parse MF API response as JSON: {response.text}")
                return {
                    "found": False,
                    "status_code": 200,
                    "message": f"Invalid JSON response from MF API: {str(e)}",
                    "raw_response": response.text
                }
