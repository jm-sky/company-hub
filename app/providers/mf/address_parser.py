"""
MF Address Parser - Robust parsing of Polish address strings from MF API.

The MF API sometimes returns address data as strings instead of structured objects.
This parser handles various Polish address formats with error handling and fallbacks.

Example inputs:
    "KOŚCIUSZKI 10, 05-220 MARKI"
    "UL. JANA PAWŁA II 15/3, 00-124 WARSZAWA"
    "AL. JEROZOLIMSKIE 142, 02-305 WARSZAWA"
    "PLAC KONSTYTUCJI 1, 00-647 WARSZAWA"
"""

import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)


def parse_mf_address(address: str) -> Dict[str, str]:
    """
    Parse MF address string into structured components.

    Args:
        address: Address string from MF API

    Returns:
        Dict with parsed address components
    """
    if not address or not isinstance(address, str):
        logger.warning(f"Invalid address input: {address}")
        return _create_empty_address()

    address = address.strip()
    if not address:
        return _create_empty_address()

    try:
        return _parse_address_components(address)
    except Exception as e:
        logger.error(f"Error parsing address '{address}': {str(e)}")
        return _create_fallback_address(address)


def _parse_address_components(address: str) -> Dict[str, str]:
    """Parse address components with robust error handling."""

    # Split by comma to separate street from city/postal code
    parts = [part.strip() for part in address.split(',')]

    if len(parts) != 2:
        logger.debug(f"Unexpected address format (no comma or multiple commas): {address}")
        return _create_fallback_address(address)

    street_part, city_part = parts

    if not street_part or not city_part:
        logger.debug(f"Empty street or city part: {address}")
        return _create_fallback_address(address)

    # Parse street component
    street_info = _parse_street_component(street_part)

    # Parse city and postal code
    city_info = _parse_city_component(city_part)

    return {
        **street_info,
        **city_info,
        "country": "Polska"
    }


def _parse_street_component(street_part: str) -> Dict[str, str]:
    """Parse street name and building/apartment numbers."""

    # Clean up common street prefixes
    street_part = _normalize_street_prefix(street_part)

    # Try to extract building and apartment numbers
    # Pattern: street name + number + optional apartment number

    # Look for patterns like "15/3" (building/apartment)
    apartment_match = re.search(r'(\d+)/(\d+)', street_part)
    if apartment_match:
        building_num = apartment_match.group(1)
        apartment_num = apartment_match.group(2)
        # Remove the building/apartment number to get street name
        street_name = street_part[:apartment_match.start()].strip()
        return {
            "street": street_name,
            "building_number": building_num,
            "apartment_number": apartment_num
        }

    # Look for simple building number pattern at the end
    building_match = re.search(r'\s+(\d+(?:[A-Z]?))\s*$', street_part)
    if building_match:
        building_num = building_match.group(1)
        street_name = street_part[:building_match.start()].strip()
        return {
            "street": street_name,
            "building_number": building_num,
            "apartment_number": ""
        }

    # Look for number anywhere in the string (fallback)
    number_match = re.search(r'\b(\d+(?:[A-Z]?))\b', street_part)
    if number_match:
        building_num = number_match.group(1)
        # Remove the number to get street name
        street_name = street_part.replace(building_num, '').strip()
        # Clean up any double spaces
        street_name = re.sub(r'\s+', ' ', street_name)
        return {
            "street": street_name,
            "building_number": building_num,
            "apartment_number": ""
        }

    # If no number pattern found, treat whole thing as street name
    logger.debug(f"No building number found in street: {street_part}")
    return {
        "street": street_part.strip(),
        "building_number": "",
        "apartment_number": ""
    }


def _parse_city_component(city_part: str) -> Dict[str, str]:
    """Parse city name and postal code."""

    # Look for postal code pattern (XX-XXX)
    postal_match = re.search(r'(\d{2}-\d{3})', city_part)
    if postal_match:
        postal_code = postal_match.group(1)
        # Remove postal code to get city name
        city_name = city_part.replace(postal_code, '').strip()
        return {
            "city": city_name,
            "postal_code": postal_code
        }

    # If no postal code found, treat whole thing as city
    logger.debug(f"No postal code found in city part: {city_part}")
    return {
        "city": city_part.strip(),
        "postal_code": ""
    }


def _normalize_street_prefix(street_part: str) -> str:
    """Normalize common Polish street prefixes."""

    # Common Polish street type abbreviations
    prefixes = [
        ('UL.', 'ULICA'),
        ('AL.', 'ALEJA'),
        ('PL.', 'PLAC'),
        ('BULW.', 'BULWAR'),
        ('OS.', 'OSIEDLE'),
        ('PARK.', 'PARK'),
        ('ROND.', 'RONDO'),
    ]

    street_upper = street_part.upper()
    for abbrev, full in prefixes:
        if street_upper.startswith(abbrev + ' '):
            # Remove the prefix for easier parsing
            return street_part[len(abbrev):].strip()

    return street_part


def _create_empty_address() -> Dict[str, str]:
    """Create empty address structure."""
    return {
        "street": "",
        "building_number": "",
        "apartment_number": "",
        "city": "",
        "postal_code": "",
        "country": "Polska"
    }


def _create_fallback_address(raw_address: str) -> Dict[str, str]:
    """Create fallback address when parsing fails."""
    return {
        "street": "",
        "building_number": "",
        "apartment_number": "",
        "city": "",
        "postal_code": "",
        "country": "Polska",
        "raw_address": raw_address  # Preserve original for debugging
    }


def validate_parsed_address(parsed: Dict[str, str]) -> bool:
    """Validate that parsed address has meaningful content."""
    required_fields = ["street", "city"]
    return any(parsed.get(field, "").strip() for field in required_fields)
