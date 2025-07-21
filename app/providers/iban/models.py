"""Data models for IBAN enrichment services."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BankDetails:
    """Bank details extracted from IBAN validation."""

    # Basic bank information
    bank_name: str = ""
    bank_code: str = ""
    branch_code: str = ""
    bic: str = ""  # BIC/SWIFT code

    # Address information (if available)
    bank_address: str = ""
    bank_city: str = ""
    bank_country: str = ""
    bank_country_code: str = ""

    # Account information
    account_number: str = ""
    iban: str = ""

    # Validation status
    is_valid: bool = False

    # Additional metadata
    currency: str = ""
    source_api: str = ""
    enriched_at: str = ""

    def __post_init__(self):
        if not self.enriched_at:
            self.enriched_at = datetime.now().isoformat()


@dataclass
class IbanValidationResult:
    """Result of IBAN validation with enrichment data."""

    original_iban: str
    formatted_iban: str = ""
    is_valid: bool = False
    bank_details: Optional[BankDetails] = None
    error_message: str = ""
    validation_source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "original_iban": self.original_iban,
            "formatted_iban": self.formatted_iban,
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "validation_source": self.validation_source,
        }

        if self.bank_details:
            result["bank_details"] = {
                "bank_name": self.bank_details.bank_name,
                "bank_code": self.bank_details.bank_code,
                "branch_code": self.bank_details.branch_code,
                "bic": self.bank_details.bic,
                "bank_address": self.bank_details.bank_address,
                "bank_city": self.bank_details.bank_city,
                "bank_country": self.bank_details.bank_country,
                "bank_country_code": self.bank_details.bank_country_code,
                "account_number": self.bank_details.account_number,
                "currency": self.bank_details.currency,
                "enriched_at": self.bank_details.enriched_at,
            }

        return result
