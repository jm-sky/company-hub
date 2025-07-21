"""IBAN enrichment client with multiple provider support and fallbacks."""

import logging
from typing import Dict, Any, Optional
from .models import IbanValidationResult
from .openiban_api import OpenIBANAPI
from .apilayer_api import APILayerBankDataAPI
from .ibanapi_com import IbanApiComClient

logger = logging.getLogger(__name__)


class IbanEnrichmentClient:
    """
    IBAN enrichment client with multiple API providers and intelligent fallbacks.

    Uses IbanApi.com as primary (free tier available) with OpenIBAN and APILayer as fallbacks.
    """

    def __init__(self, ibanapi_com_key: Optional[str] = None, apilayer_api_key: Optional[str] = None):
        self.ibanapi_com = IbanApiComClient(api_key=ibanapi_com_key) if ibanapi_com_key else None
        self.openiban_api = OpenIBANAPI()
        self.apilayer_api = APILayerBankDataAPI(api_key=apilayer_api_key)


    async def enrich_bank_account(self, account_number: str) -> Dict[str, Any]:
        """
        Enrich bank account with IBAN validation and bank details.

        Args:
            account_number: Bank account number (IBAN format expected)

        Returns:
            Dict with enrichment data including bank name, BIC, validation status
        """

        if not account_number or not isinstance(account_number, str):
            logger.debug(f"Invalid account number: {account_number}")
            return self._create_empty_enrichment(account_number, "Invalid account number")

        # Clean and validate IBAN format
        clean_iban = account_number.replace(" ", "").upper()

        if not self._is_valid_iban_format(clean_iban):
            logger.debug(f"Invalid IBAN format: {clean_iban}")
            return self._create_empty_enrichment(account_number, "Invalid IBAN format")

        # Try primary API (IbanApi.com - free tier with API key)
        if self.ibanapi_com:
            try:
                result = await self.ibanapi_com.validate_iban(clean_iban)
                logger.debug(f"IbanApi.com result for {clean_iban}: valid={result.is_valid}, has_bank_details={result.bank_details is not None}")

                if result.is_valid and result.bank_details:
                    logger.debug(f"Successfully enriched IBAN {clean_iban} using IbanApi.com")
                    return self._format_enrichment_result(result)
                elif result.is_valid:
                    logger.debug(f"IbanApi.com validated IBAN {clean_iban} but no bank details available")

            except Exception as e:
                logger.warning(f"IbanApi.com API failed for IBAN {clean_iban}: {str(e)}")

        # Try fallback API (OpenIBAN - free)
        try:
            result = await self.openiban_api.validate_iban(clean_iban)
            logger.debug(f"OpenIBAN result for {clean_iban}: valid={result.is_valid}, has_bank_details={result.bank_details is not None}")

            if result.is_valid and result.bank_details:
                logger.debug(f"Successfully enriched IBAN {clean_iban} using OpenIBAN")
                return self._format_enrichment_result(result)
            elif result.is_valid:
                logger.debug(f"OpenIBAN validated IBAN {clean_iban} but no bank details available")

        except Exception as e:
            logger.warning(f"OpenIBAN API failed for IBAN {clean_iban}: {str(e)}")

        # Try final fallback API (APILayer - paid)
        try:
            result = await self.apilayer_api.validate_iban(clean_iban)
            logger.debug(f"APILayer result for {clean_iban}: valid={result.is_valid}, has_bank_details={result.bank_details is not None}")

            if result.is_valid and result.bank_details:
                logger.debug(f"Successfully enriched IBAN {clean_iban} using APILayer")
                return self._format_enrichment_result(result)
            elif result.is_valid:
                logger.debug(f"APILayer validated IBAN {clean_iban} but no bank details available")

        except Exception as e:
            logger.warning(f"APILayer API failed for IBAN {clean_iban}: {str(e)}")

        # Both APIs failed
        logger.error(f"All IBAN enrichment APIs failed for {clean_iban}")
        return self._create_empty_enrichment(account_number, "Enrichment APIs unavailable")

    def _is_valid_iban_format(self, iban: str) -> bool:
        """Basic IBAN format validation."""
        if not iban or len(iban) < 15 or len(iban) > 34:
            return False

        # Check if starts with 2 letters (country code) followed by digits
        if not (iban[:2].isalpha() and iban[2:4].isdigit()):
            return False

        return True

    def _format_enrichment_result(self, result: IbanValidationResult) -> Dict[str, Any]:
        """Format validation result into enrichment data."""

        bank_details = result.bank_details
        if not bank_details:
            return self._create_empty_enrichment(result.original_iban, "No bank details available")

        return {
            "account_number": result.original_iban,
            "formatted_iban": result.formatted_iban,
            "validated": result.is_valid,
            "bank_name": bank_details.bank_name if bank_details.bank_name else None,
            "bic": bank_details.bic if bank_details.bic else None,
            "swift_code": bank_details.bic if bank_details.bic else None,  # BIC and SWIFT are the same
            "bank_code": bank_details.bank_code if bank_details.bank_code else None,
            "branch_code": bank_details.branch_code if bank_details.branch_code else None,
            "bank_city": bank_details.bank_city if bank_details.bank_city else None,
            "bank_country": bank_details.bank_country if bank_details.bank_country else None,
            "bank_country_code": bank_details.bank_country_code if bank_details.bank_country_code else None,
            "currency": bank_details.currency if bank_details.currency else None,
            "enrichment_source": bank_details.source_api if bank_details.source_api else None,
            "enriched_at": bank_details.enriched_at,
            "enrichment_available": True
        }

    def _create_empty_enrichment(self, account_number: str, reason: str = "") -> Dict[str, Any]:
        """Create empty enrichment result."""
        return {
            "account_number": account_number,
            "formatted_iban": account_number.replace(" ", "").upper() if account_number else None,
            "validated": False,
            "bank_name": None,
            "bic": None,
            "swift_code": None,
            "bank_code": None,
            "branch_code": None,
            "bank_city": None,
            "bank_country": None,
            "bank_country_code": None,
            "currency": None,
            "enrichment_source": None,
            "enriched_at": None,
            "enrichment_available": False,
            "enrichment_error": reason
        }

    async def batch_enrich_accounts(self, account_numbers: list) -> Dict[str, Dict[str, Any]]:
        """
        Enrich multiple bank accounts in batch.

        Args:
            account_numbers: List of bank account numbers

        Returns:
            Dict mapping account numbers to enrichment data
        """
        results = {}

        for account_number in account_numbers:
            if isinstance(account_number, str) and account_number.strip():
                clean_account = account_number.strip()
                results[clean_account] = await self.enrich_bank_account(clean_account)
            else:
                results[str(account_number)] = self._create_empty_enrichment(
                    str(account_number), "Invalid account number format"
                )

        return results
