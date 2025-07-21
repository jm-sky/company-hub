"""Safe parsing utilities for REGON API responses with robust type checking."""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_get_xml_text(element: ET.Element, default: str = "") -> str:
    """Safely get text content from XML element."""
    if element is None:
        return default
    text = element.text
    return text.strip() if text is not None else default


def safe_get_dict_value(data: Any, key: str, default: str = "") -> str:
    """Safely get a value from a dict-like object."""
    if not isinstance(data, dict):
        logger.warning(f"Expected dict for key '{key}', got {type(data)}")
        return default
        
    value = data.get(key, default)
    
    # Handle None or convert to string
    if value is None:
        return default
    
    return str(value).strip()


def safe_parse_regon_search_xml(xml_data: str) -> Dict[str, Any]:
    """Safely parse REGON search response XML with error handling."""
    try:
        # Try to parse the XML
        inner_root = ET.fromstring(xml_data)
        companies = inner_root.findall('.//dane')
        
        if not companies:
            return {"found": False, "message": "No companies found in XML"}
            
        # Process first company found
        company = companies[0]
        company_data = {}
        
        # Extract all child elements safely
        for child in company:
            if child.tag and child.text:
                company_data[child.tag] = child.text.strip()
            else:
                # Handle empty or None values
                company_data[child.tag] = ""
                
        if not company_data:
            return {"found": False, "message": "No company data extracted from XML"}
            
        return {"found": True, "data": company_data}
        
    except ET.ParseError as e:
        logger.error(f"Failed to parse REGON search XML: {str(e)}")
        return {"found": True, "raw_data": xml_data}
    except Exception as e:
        logger.error(f"Unexpected error parsing REGON search XML: {str(e)}")
        return {"found": False, "message": f"XML parsing error: {str(e)}"}


def safe_build_regon_company_info(nip: str, search_result: Dict[str, Any]) -> Dict[str, Any]:
    """Safely build basic company info from REGON search result with fallbacks."""
    
    if not search_result.get("found") or "data" not in search_result:
        return {
            "found": False,
            "nip": nip,
            "message": search_result.get("message", "Company not found in REGON database"),
            "fetched_at": datetime.now().isoformat(),
        }
    
    company_data = search_result["data"]
    
    # Safely extract data with type checking
    if not isinstance(company_data, dict):
        logger.error(f"Company data is not a dict: {type(company_data)}")
        return {
            "found": False,
            "nip": nip,
            "message": "Invalid company data format",
            "fetched_at": datetime.now().isoformat(),
        }
    
    # Safe field extraction
    regon = safe_get_dict_value(company_data, "Regon")
    typ = safe_get_dict_value(company_data, "Typ")
    name = safe_get_dict_value(company_data, "Nazwa")
    
    # Map entity type safely
    from .data_mapper import EntityType
    entity_type = map_regon_type_safely(typ)
    
    return {
        "found": True,
        "nip": nip,
        "regon": regon,
        "name": name,
        "entity_type": entity_type.value,
        "search_result": search_result,
        "fetched_at": datetime.now().isoformat(),
    }


def map_regon_type_safely(type_code: str) -> 'EntityType':
    """Safely map REGON type code to EntityType with fallback."""
    from .data_mapper import EntityType
    
    if not isinstance(type_code, str):
        logger.warning(f"Type code is not string: {type(type_code)}")
        return EntityType.LegalPerson
        
    type_code = type_code.strip().upper()
    
    type_mapping = {
        "P": EntityType.LegalPerson,
        "F": EntityType.NaturalPerson,
        "LP": EntityType.LocalLegalPersonUnit,
        "LF": EntityType.LocalNaturalPersonUnit,
    }
    
    mapped_type = type_mapping.get(type_code)
    if mapped_type is None:
        logger.warning(f"Unknown REGON entity type: '{type_code}', defaulting to LegalPerson")
        return EntityType.LegalPerson
        
    return mapped_type


def safe_extract_regon_report_data(response_xml: str, report_type: str) -> Dict[str, Any]:
    """Safely extract detailed data from REGON report response with comprehensive error handling."""
    
    try:
        # Basic validation
        if not response_xml or not isinstance(response_xml, str):
            logger.error("Invalid report response: empty or not string")
            return {"error": "Invalid response format", "report_type": report_type}
            
        # Check for report result presence
        if "DanePobierzPelnyRaportResult" not in response_xml:
            logger.error("Report result not found in response")
            return {"error": "No report data found", "report_type": report_type}
            
        # Try to extract and parse XML content
        try:
            # Extract inner XML content from SOAP response
            import re
            result_pattern = r"<DanePobierzPelnyRaportResult[^>]*>(.*?)</DanePobierzPelnyRaportResult>"
            match = re.search(result_pattern, response_xml, re.DOTALL)
            
            if match:
                inner_xml = match.group(1).strip()
                if inner_xml:
                    # Try to parse the inner XML
                    report_root = ET.fromstring(f"<root>{inner_xml}</root>")
                    report_data = {}
                    
                    # Extract all elements
                    for elem in report_root.iter():
                        if elem.tag != "root" and elem.text:
                            report_data[elem.tag] = elem.text.strip()
                            
                    return {
                        "report_type": report_type,
                        "data": report_data,
                        "raw_response": response_xml[:1000] + "..." if len(response_xml) > 1000 else response_xml
                    }
                    
        except ET.ParseError as e:
            logger.warning(f"Failed to parse report XML, storing as raw: {str(e)}")
            
        # Fallback to storing raw response
        return {
            "report_type": report_type,
            "raw_response": response_xml[:1000] + "..." if len(response_xml) > 1000 else response_xml
        }
        
    except Exception as e:
        logger.error(f"Unexpected error extracting REGON report data: {str(e)}")
        return {
            "error": f"Report parsing error: {str(e)}",
            "report_type": report_type
        }


def validate_regon_response_structure(response_text: str, expected_element: str) -> bool:
    """Validate that REGON response contains expected elements."""
    try:
        if not response_text or not isinstance(response_text, str):
            return False
            
        # Check for expected element presence
        if expected_element not in response_text:
            logger.debug(f"Expected element '{expected_element}' not found in response")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating REGON response structure: {str(e)}")
        return False