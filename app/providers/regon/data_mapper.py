"""Data mapper for REGON API types and responses."""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
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
        """Parse search response XML."""
        try:
            # Parse the inner XML data
            inner_root = ET.fromstring(response_xml)
            companies = inner_root.findall('.//dane')

            if companies:
                company_data = {}
                for company in companies:
                    for child in company:
                        company_data[child.tag] = child.text
                return {"found": True, "data": company_data}
            else:
                return {"found": False, "message": "No companies found"}

        except ET.ParseError:
            # If inner XML parsing fails, return raw data
            return {"found": True, "raw_data": response_xml}

    def build_basic_company_info(
        self,
        nip: str,
        search_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build basic company info from search result."""
        if not search_result["found"] or "data" not in search_result:
            return {
                "found": False,
                "nip": nip,
                "message": search_result.get("message", "Company not found in REGON database"),
                "fetched_at": datetime.now().isoformat(),
            }

        company_data = search_result["data"]
        regon = company_data.get("Regon", "")
        typ = company_data.get("Typ", "")

        # Map the type to EntityType
        entity_type = self.map_type_to_entity(typ)

        return {
            "found": True,
            "nip": nip,
            "regon": regon,
            "name": company_data.get("Nazwa", ""),
            "entity_type": entity_type.value,
            "search_result": search_result,
            "fetched_at": datetime.now().isoformat(),
        }

    def extract_detailed_data(self, response_xml: str, report_type: str) -> Dict[str, Any]:
        """Extract detailed data from report response."""
        return {
            "raw_response": response_xml,
            "report_type": report_type
        }
