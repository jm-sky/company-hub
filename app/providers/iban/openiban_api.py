"""OpenIBAN API client - free IBAN validation and enrichment service."""

import logging
import httpx
from typing import Dict, Any
from .models import BankDetails, IbanValidationResult

logger = logging.getLogger(__name__)


class OpenIBANAPI:
    """Client for OpenIBAN API - free IBAN validation service."""

    def __init__(self, timeout: int = 10):
        self.base_url = "https://openiban.com"
        self.timeout = timeout

    async def validate_iban(self, iban: str) -> IbanValidationResult:
        """Validate IBAN and get bank details using OpenIBAN API."""

        if not iban or not isinstance(iban, str):
            return IbanValidationResult(
                original_iban=str(iban),
                is_valid=False,
                error_message="Invalid IBAN input",
                validation_source="openiban"
            )

        # Clean IBAN (remove spaces)
        clean_iban = iban.replace(" ", "").upper()

        try:
            url = f"{self.base_url}/validate/{clean_iban}"
            params = {
                "getBIC": "true",
                "validateBankCode": "true"
            }

            logger.debug(f"Making OpenIBAN request to {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                logger.debug(f"OpenIBAN response: {response.status_code}")
            
            if response.status_code != 200:
                return IbanValidationResult(
                    original_iban=iban,
                    is_valid=False,
                    error_message=f"HTTP {response.status_code}: {response.text}",
                    validation_source="openiban"
                )

            data = response.json()
            logger.debug(f"OpenIBAN response data: {data}")
            return self._parse_openiban_response(iban, clean_iban, data)

        except httpx.TimeoutException:
            logger.error(f"OpenIBAN API timeout for IBAN {iban}")
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message="API timeout",
                validation_source="openiban"
            )
        except Exception as e:
            logger.error(f"OpenIBAN API error for IBAN {iban}: {str(e)}")
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message=f"API error: {str(e)}",
                validation_source="openiban"
            )

    def _parse_openiban_response(
        self,
        original_iban: str,
        clean_iban: str,
        data: Dict[str, Any]
    ) -> IbanValidationResult:
        """Parse OpenIBAN API response into our format."""

        try:
            is_valid = data.get("valid", False)

            if not is_valid:
                messages = data.get("messages", [])
                error_msg = "Invalid IBAN"
                if isinstance(messages, list) and messages:
                    error_msg = messages[0] if isinstance(messages[0], str) else "Invalid IBAN"

                return IbanValidationResult(
                    original_iban=original_iban,
                    formatted_iban=clean_iban,
                    is_valid=False,
                    error_message=error_msg,
                    validation_source="openiban"
                )

            # Extract bank details - handle actual OpenIBAN response structure
            bank_data = self._safe_get(data, "bankData", {})
            if not isinstance(bank_data, dict):
                bank_data = {}

            # Get bank name and code from bankData
            bank_name = self._safe_get(bank_data, "name", "")
            bank_code = self._safe_get(bank_data, "bankCode", "")
            
            # Check if we have meaningful bank data (OpenIBAN often returns empty values)
            has_bank_info = bool(bank_name and bank_name.strip()) or bool(bank_code and bank_code.strip())
            
            if not has_bank_info:
                logger.debug(f"OpenIBAN returned valid IBAN but no bank details for {clean_iban}")
                # Return valid IBAN but without enrichment
                return IbanValidationResult(
                    original_iban=original_iban,
                    formatted_iban=clean_iban,
                    is_valid=True,
                    bank_details=None,  # No bank details available
                    validation_source="openiban"
                )

            bank_details = BankDetails(
                iban=clean_iban,
                account_number=self._safe_get(data, "accountIdentifier", ""),
                bank_name=bank_name,
                bank_code=bank_code,
                bic=self._safe_get(bank_data, "bic", ""),
                bank_city=self._safe_get(bank_data, "city", ""),
                bank_country=self._safe_get(data, "countryCode", "")[:2] if self._safe_get(data, "countryCode") else "",
                bank_country_code=self._safe_get(data, "countryCode", "")[:2] if self._safe_get(data, "countryCode") else "",
                currency="",  # OpenIBAN doesn't provide currency in basic response
                is_valid=True,
                source_api="openiban"
            )

            return IbanValidationResult(
                original_iban=original_iban,
                formatted_iban=clean_iban,
                is_valid=True,
                bank_details=bank_details,
                validation_source="openiban"
            )

        except Exception as e:
            logger.error(f"Error parsing OpenIBAN response: {str(e)}")
            return IbanValidationResult(
                original_iban=original_iban,
                formatted_iban=clean_iban,
                is_valid=False,
                error_message=f"Response parsing error: {str(e)}",
                validation_source="openiban"
            )

    def _safe_get(self, data: Any, key: str, default: Any = None) -> Any:
        """Safely get value from nested dict structure."""
        if not isinstance(data, dict):
            return default
        return data.get(key, default)
