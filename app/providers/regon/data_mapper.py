"""Data mapper for REGON API types and responses."""

import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class EntityType(Enum):
    LegalPerson = "P"  # Osoba prawna
    NaturalPerson = "F"  # Osoba fizyczna
    LocalLegalPersonUnit = "LP"  # Jednostka lokalna osoby prawnej
    LocalNaturalPersonUnit = "LF"  # Jednostka lokalna osoby fizycznej


class RegonReportName(Enum):
    # Osoby prawne
    BIR11LegalPerson = "BIR11OsPrawna"

    # Osoby fizyczne prowadzące działalność
    BIR11NaturalPersonCeidg = "BIR11OsFizycznaDzialalnoscCeidg"
    BIR11NaturalPersonDzialalnoscPozostala = "BIR11OsFizycznaDzialalnoscPozostala"
    BIR11NaturalPersonRolnicza = "BIR11OsFizycznaRolnicza"

    # Jednostki lokalne
    BIR11LocalLegalPersonUnit = "BIR11JednLokalnaOsPrawnej"
    BIR11LocalNaturalPersonUnit = "BIR11JednLokalnaOsFizycznej"


class RegonDataMapper:
    """Maps REGON API data types and responses."""

    def __init__(self):
        # Entity type to report mapping
        self.entity_report_mapping = {
            EntityType.LegalPerson: RegonReportName.BIR11LegalPerson,
            EntityType.NaturalPerson: RegonReportName.BIR11NaturalPersonCeidg,
            EntityType.LocalLegalPersonUnit: RegonReportName.BIR11LocalLegalPersonUnit,
            EntityType.LocalNaturalPersonUnit: RegonReportName.BIR11LocalNaturalPersonUnit,
        }

    def map_type_to_entity(self, type_code: str) -> EntityType:
        """Map REGON type code to EntityType."""
        type_mapping = {
            "P": EntityType.LegalPerson,
            "F": EntityType.NaturalPerson,
            "LP": EntityType.LocalLegalPersonUnit,
            "LF": EntityType.LocalNaturalPersonUnit,
        }
        return type_mapping.get(type_code, EntityType.LegalPerson)

    def get_report_name(self, entity_type: EntityType) -> RegonReportName:
        """Get report name for entity type."""
        return self.entity_report_mapping[entity_type]

    def parse_search_response(self, response_xml: str) -> Dict[str, Any]:
        """Parse search response XML with robust error handling."""
        from .safe_parser import safe_parse_regon_search_xml
        return safe_parse_regon_search_xml(response_xml)

    def build_basic_company_info(
        self,
        nip: str,
        search_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build basic company info from search result with robust error handling."""
        from .safe_parser import safe_build_regon_company_info
        return safe_build_regon_company_info(nip, search_result)

    def extract_detailed_data(self, response_xml: str, report_type: str) -> Dict[str, Any]:
        """Extract detailed data from report response with robust error handling."""
        from .safe_parser import safe_extract_regon_report_data
        return safe_extract_regon_report_data(response_xml, report_type)
