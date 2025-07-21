"""Safe parsing utilities for MF API responses with robust type checking."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def safe_get(data: Any, key: str, default: Any = "", expected_type: type = str) -> Any:
    """Safely get a value from a dict-like object with type checking."""
    if not isinstance(data, dict):
        logger.warning(f"Expected dict for key '{key}', got {type(data)}")
        return default

    value = data.get(key, default)

    if value is None:
        return default

    if not isinstance(value, expected_type):
        logger.debug(f"Key '{key}' expected {expected_type.__name__}, got {type(value).__name__}: {value}")
        # Try to convert if possible
        if expected_type == str:
            return str(value) if value is not None else default
        elif expected_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'tak')
            return bool(value)
        elif expected_type in (int, float):
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                return default
        else:
            return default

    return value


def safe_parse_address(addr_data: Any) -> Optional[Dict[str, str]]:
    """Safely parse address data with fallbacks for different formats."""
    if not addr_data:
        return None

    if isinstance(addr_data, str):
        # Handle string addresses by attempting to parse
        logger.debug(f"Address is string format: {addr_data}")
        try:
            from .address_parser import parse_mf_address
            return parse_mf_address(addr_data)
        except Exception as e:
            logger.warning(f"Failed to parse string address '{addr_data}': {str(e)}")
            return {"raw_address": addr_data}

    if not isinstance(addr_data, dict):
        logger.warning(f"Address data is neither string nor dict: {type(addr_data)}")
        return None

    return {
        "street": safe_get(addr_data, "street"),
        "building_number": safe_get(addr_data, "buildingNumber"),
        "apartment_number": safe_get(addr_data, "apartmentNumber"),
        "city": safe_get(addr_data, "city"),
        "postal_code": safe_get(addr_data, "postalCode"),
        "country": safe_get(addr_data, "country", "Polska")
    }


async def safe_parse_bank_accounts(accounts: Any, date: str, enable_enrichment: bool = True, country_code: str = 'PL') -> List[Dict[str, Any]]:
    """Safely parse bank account numbers with type checking and optional IBAN enrichment."""
    if not accounts:
        return []

    if not isinstance(accounts, list):
        logger.warning(f"Bank accounts expected list, got {type(accounts)}: {accounts}")
        # Try to convert single string to list
        if isinstance(accounts, str):
            accounts = [accounts]
        else:
            return []

    result = []
    enrichment_client = None

    # Initialize IBAN enrichment client if enabled
    if enable_enrichment:
        try:
            from app.providers.iban import IbanEnrichmentClient
            from app.config import settings
            
            # Try to get IbanApi.com key from settings
            ibanapi_key = getattr(settings, 'ibanapi_com_key', None)
            apilayer_key = getattr(settings, 'apilayer_api_key', None)
            
            enrichment_client = IbanEnrichmentClient(
                ibanapi_com_key=ibanapi_key,
                apilayer_api_key=apilayer_key
            )
            logger.debug(f"IBAN enrichment client initialized with IbanApi.com: {bool(ibanapi_key)}, APILayer: {bool(apilayer_key)}")
        except Exception as e:
            logger.warning(f"IBAN enrichment unavailable: {str(e)}")
            enable_enrichment = False

    for account in accounts:
        if not isinstance(account, str) or not account.strip():
            logger.debug(f"Skipping invalid bank account: {account}")
            continue

        clean_account = format_bank_account_as_iban(account=account, country_code=country_code)

        # Basic account info
        account_info = {
            "account_number": clean_account,
            "validated": True,
            "date": date
        }

        # Add IBAN enrichment if enabled
        if enable_enrichment and enrichment_client:
            try:
                enrichment = await enrichment_client.enrich_bank_account(clean_account)
                account_info.update({
                    "enrichment": enrichment,
                    "bank_name": enrichment.get("bank_name"),
                    "bic": enrichment.get("bic"),
                    "swift_code": enrichment.get("swift_code"),
                    "formatted_iban": enrichment.get("formatted_iban", clean_account),
                    "enrichment_available": enrichment.get("enrichment_available", False)
                })
            except Exception as e:
                logger.warning(f"Failed to enrich account {clean_account}: {str(e)}")
                account_info.update({
                    "enrichment_available": False,
                    "enrichment_error": str(e)
                })
        else:
            account_info["enrichment_available"] = False

        result.append(account_info)

    return result


def safe_parse_person_list(persons: Any, list_type: str) -> List[Dict[str, str]]:
    """Safely parse person lists (representatives, authorized persons, partners)."""
    if not persons:
        return []

    if not isinstance(persons, list):
        logger.warning(f"{list_type} expected list, got {type(persons)}: {persons}")
        return []

    result = []
    for person in persons:
        if not isinstance(person, dict):
            logger.debug(f"Skipping invalid {list_type} entry: {person}")
            continue

        parsed_person = {
            "company_name": safe_get(person, "companyName"),
            "first_name": safe_get(person, "firstName"),
            "last_name": safe_get(person, "lastName"),
            "nip": safe_get(person, "nip"),
            "pesel": safe_get(person, "pesel")
        }

        # Only add if at least one field has meaningful data
        if any(value.strip() for value in parsed_person.values() if isinstance(value, str)):
            result.append(parsed_person)
        else:
            logger.debug(f"Skipping empty {list_type} entry")

    return result


def safe_parse_mf_subject(subject: Any) -> Dict[str, Any]:
    """Safely parse MF subject data with comprehensive error handling."""
    if not isinstance(subject, dict):
        logger.error(f"Subject data is not a dict: {type(subject)}")
        raise ValueError(f"Invalid subject data type: {type(subject)}")

    # Basic fields with safe extraction
    basic_data = {
        "name": safe_get(subject, "name"),
        "regon": safe_get(subject, "regon"),
        "krs": safe_get(subject, "krs"),
        "status_vat": safe_get(subject, "statusVat"),
        "registration_legal_date": safe_get(subject, "registrationLegalDate"),
        "registration_denial_basis": safe_get(subject, "registrationDenialBasis"),
        "registration_denial_date": safe_get(subject, "registrationDenialDate"),
        "restoration_basis": safe_get(subject, "restorationBasis"),
        "restoration_date": safe_get(subject, "restorationDate"),
        "removal_basis": safe_get(subject, "removalBasis"),
        "removal_date": safe_get(subject, "removalDate"),
        "has_virtual_accounts": safe_get(subject, "hasVirtualAccounts", False, bool),
    }

    # Complex fields with custom parsing
    complex_data = {
        "address": safe_parse_address(subject.get("workingAddress")),
        "residence_address": safe_parse_address(subject.get("residenceAddress")),
        "representatives": safe_parse_person_list(subject.get("representatives"), "representatives"),
        "authorized_persons": safe_parse_person_list(subject.get("authorizedClerks"), "authorized_persons"),
        "partners": safe_parse_person_list(subject.get("partners"), "partners"),
    }

    # Merge all data
    return {**basic_data, **complex_data}


def validate_mf_response_structure(data: Dict[str, Any]) -> bool:
    """Validate that MF response has the expected structure."""
    try:
        if not isinstance(data, dict):
            logger.error(f"MF response is not a dict: {type(data)}")
            return False

        if "result" not in data:
            logger.error("MF response missing 'result' field")
            return False

        result = data["result"]
        if not isinstance(result, dict):
            logger.error(f"MF result is not a dict: {type(result)}")
            return False

        # Check for either subject or subjects field
        has_subject = "subject" in result
        has_subjects = "subjects" in result

        if not has_subject and not has_subjects:
            logger.info("MF result has no subject/subjects field (likely no data found)")

        return True

    except Exception as e:
        logger.error(f"Error validating MF response structure: {str(e)}")
        return False


def format_bank_account_as_iban(account: str, country_code: str = 'PL') -> str:
    """Format bank account as IBAN."""
    account = account.replace(" ", "").upper().strip()

    if account.startswith(country_code):
        return account

    return f'{country_code}{account}'.strip()
