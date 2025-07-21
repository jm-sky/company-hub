"""IbanApi.com client - matches the PHP implementation."""

import logging
import httpx
from typing import Dict, Any
from .models import BankDetails, IbanValidationResult

logger = logging.getLogger(__name__)


class IbanApiComClient:
    """Client for IbanApi.com API - matches PHP implementation."""

    def __init__(self, api_key: str, timeout: int = 10):
        self.base_url = "https://api.ibanapi.com/v1"
        self.api_key = api_key
        self.timeout = timeout

    async def validate_iban(self, iban: str) -> IbanValidationResult:
        """Validate IBAN and get bank details using IbanApi.com API."""

        if not iban or not isinstance(iban, str):
            return IbanValidationResult(
                original_iban=str(iban),
                is_valid=False,
                error_message="Invalid IBAN input",
                validation_source="ibanapi_com"
            )

        # Clean IBAN (remove spaces)
        clean_iban = iban.replace(" ", "").upper()

        try:
            url = f"{self.base_url}/validate"
            params = {
                "api_key": self.api_key,
                "iban": clean_iban
            }

            logger.debug(f"Making IbanApi.com request to {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                logger.debug(f"IbanApi.com response: {response.status_code}")

                if response.status_code != 200:
                    return IbanValidationResult(
                        original_iban=iban,
                        is_valid=False,
                        error_message=f"HTTP {response.status_code}: {response.text}",
                        validation_source="ibanapi_com"
                    )

                data = response.json()
                logger.debug(f"IbanApi.com response data: {data}")
                return self._parse_ibanapi_response(iban, clean_iban, data)

        except httpx.TimeoutException:
            logger.error(f"IbanApi.com API timeout for IBAN {iban}")
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message="API timeout",
                validation_source="ibanapi_com"
            )
        except Exception as e:
            logger.error(f"IbanApi.com API error for IBAN {iban}: {str(e)}")
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message=f"API error: {str(e)}",
                validation_source="ibanapi_com"
            )

    def _parse_ibanapi_response(
        self,
        original_iban: str,
        clean_iban: str,
        data: Dict[str, Any]
    ) -> IbanValidationResult:
        """Parse IbanApi.com API response - matches PHP DTO structure."""

        try:
            # IbanApi.com response structure based on PHP DTOs
            result = self._safe_get(data, "result", 0)
            message = self._safe_get(data, "message", "")

            # Check if result indicates success (200 = HTTP success, not 1)
            is_valid = result == 200

            if not is_valid:
                return IbanValidationResult(
                    original_iban=original_iban,
                    formatted_iban=clean_iban,
                    is_valid=False,
                    error_message=message or "Invalid IBAN",
                    validation_source="ibanapi_com"
                )

            # Extract data section (matches IbanDataDTO structure)
            iban_data = self._safe_get(data, "data", {})
            if not isinstance(iban_data, dict):
                iban_data = {}

            # Extract bank details (matches BankDTO structure)
            bank_data = self._safe_get(iban_data, "bank", {})
            if not isinstance(bank_data, dict):
                bank_data = {}

            bank_name = self._safe_get(bank_data, "bank_name", "")
            bic = self._safe_get(bank_data, "bic", "")

            # Check if we have meaningful bank data
            has_bank_info = bool(bank_name and bank_name.strip()) or bool(bic and bic.strip())

            if not has_bank_info:
                logger.debug(f"IbanApi.com returned valid IBAN but no bank details for {clean_iban}")
                return IbanValidationResult(
                    original_iban=original_iban,
                    formatted_iban=clean_iban,
                    is_valid=True,
                    bank_details=None,
                    validation_source="ibanapi_com"
                )

            bank_details = BankDetails(
                iban=clean_iban,
                account_number=self._safe_get(iban_data, "bank_account", ""),
                bank_name=bank_name,
                bank_code="",  # Not provided in IbanApi.com response
                bic=bic,
                branch_code="",  # Not provided
                bank_city=self._safe_get(bank_data, "city", ""),
                bank_country=self._safe_get(iban_data, "country_name", ""),
                bank_country_code=self._safe_get(iban_data, "country_code", ""),
                currency=self._safe_get(iban_data, "currency_code", ""),
                is_valid=True,
                source_api="ibanapi_com"
            )

            return IbanValidationResult(
                original_iban=original_iban,
                formatted_iban=clean_iban,
                is_valid=True,
                bank_details=bank_details,
                validation_source="ibanapi_com"
            )

        except Exception as e:
            logger.error(f"Error parsing IbanApi.com response: {str(e)}")
            return IbanValidationResult(
                original_iban=original_iban,
                formatted_iban=clean_iban,
                is_valid=False,
                error_message=f"Response parsing error: {str(e)}",
                validation_source="ibanapi_com"
            )

    def _safe_get(self, data: Any, key: str, default: Any = None) -> Any:
        """Safely get value from nested dict structure."""
        if not isinstance(data, dict):
            return default
        return data.get(key, default)
