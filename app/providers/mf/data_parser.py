"""Data parser for MF API responses with robust error handling."""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
from .safe_parser import (
    safe_parse_mf_subject,
    safe_parse_bank_accounts,
    validate_mf_response_structure
)

logger = logging.getLogger(__name__)


class MfDataParser:
    """Parses MF API response data into structured format with robust error handling."""

    async def parse_response(self, data: Dict[str, Any], nip: str, date: str) -> Dict[str, Any]:
        """Parse MF API response with comprehensive error handling."""

        # Validate basic response structure
        if not validate_mf_response_structure(data):
            return self._create_not_found_response(nip, date, "Invalid response format from MF API")

        result = data["result"]

        # Handle case where no subject data found
        if not result or "subject" not in result:
            logger.info(f"MF API result structure: {result}")
            return self._create_not_found_response(nip, date, "No subject data found in MF response")

        subject = result["subject"]

        try:
            # Use safe parsing for subject data
            subject_data = safe_parse_mf_subject(subject)

            # Add bank accounts with safe parsing and IBAN enrichment
            bank_accounts = await safe_parse_bank_accounts(subject.get("accountNumbers"), date)

            return {
                "found": True,
                "nip": nip,
                "date": date,
                "request_id": data.get("requestId", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "bank_accounts": bank_accounts,
                **subject_data
            }

        except Exception as e:
            logger.error(f"Error parsing MF response for NIP {nip}: {str(e)}", exc_info=True)
            return self._create_not_found_response(nip, date, f"Error parsing MF response: {str(e)}")

    def _create_not_found_response(self, nip: str, date: str, message: str) -> Dict[str, Any]:
        """Create a standardized not found response."""
        return {
            "found": False,
            "nip": nip,
            "date": date,
            "message": message,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
