import re
from typing import Optional


def validate_nip(nip: str) -> bool:
    """
    Validate Polish NIP (Tax Identification Number).

    Args:
        nip: NIP number as string

    Returns:
        bool: True if valid, False otherwise
    """
    if not nip:
        return False

    # Remove any non-digit characters
    nip_clean = re.sub(r"\D", "", nip)

    # NIP must be exactly 10 digits
    if len(nip_clean) != 10:
        return False

    # Check if all digits are the same (invalid)
    if len(set(nip_clean)) == 1:
        return False

    # Calculate checksum
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    checksum = sum(int(digit) * weight for digit, weight in zip(nip_clean[:9], weights))

    # Check if checksum modulo 11 equals the last digit
    return (checksum % 11) == int(nip_clean[9])


def normalize_nip(nip: str) -> Optional[str]:
    """
    Normalize NIP to standard format (10 digits).

    Args:
        nip: NIP number as string

    Returns:
        str: Normalized NIP or None if invalid
    """
    if not nip:
        return None

    # Remove any non-digit characters
    nip_clean = re.sub(r"\D", "", nip)

    if validate_nip(nip_clean):
        return nip_clean

    return None


def validate_regon(regon: str) -> bool:
    """
    Validate Polish REGON number.

    Args:
        regon: REGON number as string

    Returns:
        bool: True if valid, False otherwise
    """
    if not regon:
        return False

    # Remove any non-digit characters
    regon_clean = re.sub(r"\D", "", regon)

    # REGON can be 9 or 14 digits
    if len(regon_clean) not in [9, 14]:
        return False

    # Validate 9-digit REGON
    if len(regon_clean) == 9:
        weights = [8, 9, 2, 3, 4, 5, 6, 7]
        checksum = sum(
            int(digit) * weight for digit, weight in zip(regon_clean[:8], weights)
        )
        return (checksum % 11) % 10 == int(regon_clean[8])

    # Validate 14-digit REGON
    if len(regon_clean) == 14:
        # First validate the 9-digit part
        if not validate_regon(regon_clean[:9]):
            return False

        # Then validate the full 14-digit number
        weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
        checksum = sum(
            int(digit) * weight for digit, weight in zip(regon_clean[:13], weights)
        )
        return (checksum % 11) % 10 == int(regon_clean[13])

    return False
