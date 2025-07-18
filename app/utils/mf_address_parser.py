"""
 Example input:
    KOŚCIUSZKI 10, 05-220 MARKI
"""
def parse_mf_address(address: str) -> dict:
    """Parse MF address."""
    # Split the address into parts
    [street_with_number, city_with_postal_code] = address.split(",")

    if not street_with_number or not city_with_postal_code:
        return {
            "street": address,
            "building_number": "",
            "apartment_number": "",
            "city": "",
            "postal_code": "",
            "country": "Polska"
        }

    street_parts = street_with_number.split(" ")
    city_parts = city_with_postal_code.split(" ")

    if len(street_parts) == 1:
        street_parts.append("")
        street_parts.append("")
    elif len(street_parts) == 2:
        street_parts.append("")

    if len(city_parts) == 1:
        city_parts.append("")
        city_parts.append("")
    elif len(city_parts) == 2:
        city_parts.append("")

    return {
        "street": street_parts[0] if street_parts[0] else address,
        "building_number": street_parts[1] if street_parts[1] else "",
        "apartment_number": street_parts[2] if street_parts[2] else "",
        "city": city_parts[0] if city_parts[0] else "",
        "postal_code": city_parts[1] if city_parts[1] else "",
        "country": "Polska"
    }
