"""Data parser for MF API responses."""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.utils.mf_address_parser import parse_mf_address

logger = logging.getLogger(__name__)


class MfDataParser:
    """Parses MF API response data into structured format."""

    def parse_response(self, data: Dict[str, Any], nip: str, date: str) -> Dict[str, Any]:
        """Parse MF API response."""

        if not isinstance(data, dict):
            logger.error(f"MF API returned non-dict response: {type(data)}")
            return self._create_not_found_response(nip, date, "Invalid response format from MF API")

        if "result" not in data:
            logger.error(f"MF API response missing 'result' field: {data}")
            return self._create_not_found_response(nip, date, "Missing result field in MF API response")

        result = data["result"]

        if not result or "subject" not in result:
            logger.info(f"MF API result structure: {result}")
            return self._create_not_found_response(nip, date, "No subject data found in MF response")

        subject = result["subject"]

        try:
            return self._parse_subject_data(subject, nip, date, data.get("requestId", ""))
        except Exception as e:
            logger.error(f"Error parsing MF response: {str(e)}")
            return self._create_not_found_response(nip, date, f"Error parsing MF response: {str(e)}")

    def _create_not_found_response(self, nip: str, date: str, message: str) -> Dict[str, Any]:
        """Create a standardized not found response."""
        return {
            "found": False,
            "nip": nip,
            "date": date,
            "message": message,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }

    def _parse_subject_data(self, subject: Dict[str, Any], nip: str, date: str, request_id: str) -> Dict[str, Any]:
        """Parse subject data from MF response."""

        return {
            "found": True,
            "nip": nip,
            "date": date,
            "name": subject.get("name", ""),
            "regon": subject.get("regon", ""),
            "krs": subject.get("krs", ""),
            "status_vat": subject.get("statusVat", ""),
            "registration_legal_date": subject.get("registrationLegalDate", ""),
            "registration_denial_basis": subject.get("registrationDenialBasis", ""),
            "registration_denial_date": subject.get("registrationDenialDate", ""),
            "restoration_basis": subject.get("restorationBasis", ""),
            "restoration_date": subject.get("restorationDate", ""),
            "removal_basis": subject.get("removalBasis", ""),
            "removal_date": subject.get("removalDate", ""),
            "address": self._parse_working_address(subject.get("workingAddress")),
            "residence_address": self._parse_residence_address(subject.get("residenceAddress")),
            "bank_accounts": self._parse_bank_accounts(subject.get("accountNumbers", []), date),
            "representatives": self._parse_representatives(subject.get("representatives", [])),
            "authorized_persons": self._parse_authorized_persons(subject.get("authorizedClerks", [])),
            "partners": self._parse_partners(subject.get("partners", [])),
            "has_virtual_accounts": subject.get("hasVirtualAccounts", False),
            "request_id": request_id,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }

    def _parse_working_address(self, addr_data: Any) -> Dict[str, str]:
        """Parse working address data."""
        if not addr_data:
            return None

        return {
            "street": addr_data.get("street", ""),
            "building_number": addr_data.get("buildingNumber", ""),
            "apartment_number": addr_data.get("apartmentNumber", ""),
            "city": addr_data.get("city", ""),
            "postal_code": addr_data.get("postalCode", ""),
            "country": addr_data.get("country", "Polska")
        }

    def _parse_residence_address(self, addr_data: Any) -> Dict[str, str]:
        """Parse residence address data."""
        if not addr_data:
            return None

        if isinstance(addr_data, dict):
            return {
                "street": addr_data.get("street", ""),
                "building_number": addr_data.get("buildingNumber", ""),
                "apartment_number": addr_data.get("apartmentNumber", ""),
                "city": addr_data.get("city", ""),
                "postal_code": addr_data.get("postalCode", ""),
                "country": addr_data.get("country", "Polska")
            }
        elif isinstance(addr_data, str):
            return parse_mf_address(addr_data)

        return None

    def _parse_bank_accounts(self, accounts: List[str], date: str) -> List[Dict[str, Any]]:
        """Parse bank account numbers."""
        if not isinstance(accounts, list):
            return []

        return [
            {
                "account_number": account,
                "validated": True,
                "date": date
            }
            for account in accounts
        ]

    def _parse_representatives(self, representatives: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Parse representatives data."""
        if not isinstance(representatives, list):
            return []

        return [
            {
                "company_name": rep.get("companyName", ""),
                "first_name": rep.get("firstName", ""),
                "last_name": rep.get("lastName", ""),
                "nip": rep.get("nip", ""),
                "pesel": rep.get("pesel", "")
            }
            for rep in representatives
        ]

    def _parse_authorized_persons(self, authorized_persons: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Parse authorized persons data."""
        if not isinstance(authorized_persons, list):
            return []

        return [
            {
                "company_name": person.get("companyName", ""),
                "first_name": person.get("firstName", ""),
                "last_name": person.get("lastName", ""),
                "nip": person.get("nip", ""),
                "pesel": person.get("pesel", "")
            }
            for person in authorized_persons
        ]

    def _parse_partners(self, partners: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Parse business partners data."""
        if not isinstance(partners, list):
            return []

        return [
            {
                "company_name": partner.get("companyName", ""),
                "first_name": partner.get("firstName", ""),
                "last_name": partner.get("lastName", ""),
                "nip": partner.get("nip", ""),
                "pesel": partner.get("pesel", "")
            }
            for partner in partners
        ]
