"""APILayer Bank Data API client - professional IBAN validation service."""

import logging
import httpx
from typing import Dict, Any, Optional
from .models import BankDetails, IbanValidationResult

logger = logging.getLogger(__name__)


class APILayerBankDataAPI:
    """Client for APILayer Bank Data API - professional IBAN validation service."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.base_url = "https://api.apilayer.com/bank_data"
        self.api_key = api_key
        self.timeout = timeout

    async def validate_iban(self, iban: str) -> IbanValidationResult:
        """Validate IBAN and get bank details using APILayer Bank Data API."""

        if not self.api_key:
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message="APILayer API key not configured",
                validation_source="apilayer"
            )

        if not iban or not isinstance(iban, str):
            return IbanValidationResult(
                original_iban=str(iban),
                is_valid=False,
                error_message="Invalid IBAN input",
                validation_source="apilayer"
            )

        # Clean IBAN (remove spaces)
        clean_iban = iban.replace(" ", "").upper()

        try:
            url = f"{self.base_url}/iban_validate"
            params = {"iban": clean_iban}
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }

            logger.debug(f"Making APILayer request to {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)

                logger.debug(f"APILayer response: {response.status_code}")

                if response.status_code == 429:
                    return IbanValidationResult(
                        original_iban=iban,
                        is_valid=False,
                        error_message="API rate limit exceeded",
                        validation_source="apilayer"
                    )

                if response.status_code == 401:
                    return IbanValidationResult(
                        original_iban=iban,
                        is_valid=False,
                        error_message="Invalid API key",
                        validation_source="apilayer"
                    )

                if response.status_code != 200:
                    return IbanValidationResult(
                        original_iban=iban,
                        is_valid=False,
                        error_message=f"HTTP {response.status_code}: {response.text}",
                        validation_source="apilayer"
                    )

                data = response.json()
                return self._parse_apilayer_response(iban, clean_iban, data)

        except httpx.TimeoutException:
            logger.error(f"APILayer API timeout for IBAN {iban}")
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message="API timeout",
                validation_source="apilayer"
            )
        except Exception as e:
            logger.error(f"APILayer API error for IBAN {iban}: {str(e)}")
            return IbanValidationResult(
                original_iban=iban,
                is_valid=False,
                error_message=f"API error: {str(e)}",
                validation_source="apilayer"
            )

    def _parse_apilayer_response(
        self,
        original_iban: str,
        clean_iban: str,
        data: Dict[str, Any]
    ) -> IbanValidationResult:
        """Parse APILayer API response into our format."""

        try:
            is_valid = data.get("valid", False)

            if not is_valid:
                return IbanValidationResult(
                    original_iban=original_iban,
                    formatted_iban=clean_iban,
                    is_valid=False,
                    error_message=data.get("error", {}).get("info", "Invalid IBAN"),
                    validation_source="apilayer"
                )

            # Extract bank details from APILayer response
            bank_details = BankDetails(
                iban=clean_iban,
                account_number=self._safe_get(data, "account_number", ""),
                bank_name=self._safe_get(data, "bank_name", ""),
                bank_code=self._safe_get(data, "bank_code", ""),
                branch_code=self._safe_get(data, "branch_code", ""),
                bic=self._safe_get(data, "bic", ""),
                bank_address=self._safe_get(data, "bank_address", ""),
                bank_city=self._safe_get(data, "bank_city", ""),
                bank_country=self._safe_get(data, "country", ""),
                bank_country_code=self._safe_get(data, "country_code", ""),
                currency=self._safe_get(data, "currency", ""),
                is_valid=True,
                source_api="apilayer"
            )

            return IbanValidationResult(
                original_iban=original_iban,
                formatted_iban=clean_iban,
                is_valid=True,
                bank_details=bank_details,
                validation_source="apilayer"
            )

        except Exception as e:
            logger.error(f"Error parsing APILayer response: {str(e)}")
            return IbanValidationResult(
                original_iban=original_iban,
                formatted_iban=clean_iban,
                is_valid=False,
                error_message=f"Response parsing error: {str(e)}",
                validation_source="apilayer"
            )

    def _safe_get(self, data: Any, key: str, default: Any = "") -> Any:
        """Safely get value from dict structure."""
        if not isinstance(data, dict):
            return default
        return data.get(key, default)
