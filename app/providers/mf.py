"""MF (Biała Lista) data provider implementation."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import httpx

from app.providers.base import BaseProvider, ProviderError, RateLimitError, ValidationError
from app.utils.validators import validate_nip

logger = logging.getLogger(__name__)


class MfProvider(BaseProvider):
    """Provider for MF (Biała Lista) - Polish VAT whitelist."""

    def __init__(self, api_url: str = "https://wl-api.mf.gov.pl"):
        super().__init__("MF")
        self.api_url = api_url.rstrip("/")
        self.rate_limit_window = timedelta(seconds=1)  # 1 request per second
        self.timeout = 10

    def validate_identifier(self, identifier: str) -> bool:
        """Validate NIP for MF API."""
        return validate_nip(identifier)

    def is_rate_limited(self) -> bool:
        """Check if we're rate limited."""
        if not self.last_request_time:
            return False
        return datetime.now(timezone.utc) - self.last_request_time < self.rate_limit_window

    def get_next_available_time(self) -> Optional[datetime]:
        """Get next available time for requests."""
        if not self.is_rate_limited():
            return None
        return self.last_request_time + self.rate_limit_window if self.last_request_time else None

    async def fetch_data(self, nip: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch company data from MF API.

        Args:
            nip: Company NIP number
            **kwargs: Additional parameters (date for historical data)

        Returns:
            Dict containing MF data
        """
        if not self.validate_identifier(nip):
            raise ValidationError(f"Invalid NIP: {nip}", self.name)

        if self.is_rate_limited():
            raise RateLimitError(self.name, self.get_next_available_time())

        # Get date parameter (format: YYYY-MM-DD)
        date_param = kwargs.get("date")
        if not date_param:
            date_param = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Clean NIP (remove dashes)
        clean_nip = nip.replace("-", "")

        url = f"{self.api_url}/api/search/nip/{clean_nip}"
        params = {"date": date_param}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"MF API request: {url} with params: {params}")

                response = await client.get(url, params=params)
                self.last_request_time = datetime.now(timezone.utc)

                logger.info(f"MF API response: {response.status_code}")

                if response.status_code == 404:
                    return {
                        "found": False,
                        "nip": nip,
                        "date": date_param,
                        "message": "Company not found in MF whitelist",
                        "fetched_at": datetime.now(timezone.utc).isoformat()
                    }

                if response.status_code == 429:
                    raise RateLimitError(self.name)

                response.raise_for_status()

                # Try to parse JSON response
                try:
                    data = response.json()
                except Exception as e:
                    logger.error(f"Failed to parse MF API response as JSON: {response.text}")
                    raise ProviderError(f"Invalid JSON response from MF API: {str(e)}", self.name)

                # Parse MF response
                result = self._parse_mf_response(data, nip, date_param)
                return result

        except httpx.TimeoutException:
            raise ProviderError(f"MF API timeout for NIP {nip}", self.name, 408)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitError(self.name)
            raise ProviderError(f"MF API error: {e.response.status_code}", self.name, e.response.status_code)
        except Exception as e:
            logger.error(f"MF API error for NIP {nip}: {str(e)}")
            raise ProviderError(f"MF API error: {str(e)}", self.name)

    def _parse_mf_response(self, data: Dict[str, Any], nip: str, date: str) -> Dict[str, Any]:
        """Parse MF API response."""
        logger.debug(f"Parsing MF response: {data}")

        if not isinstance(data, dict):
            logger.error(f"MF API returned non-dict response: {type(data)}")
            return {
                "found": False,
                "nip": nip,
                "date": date,
                "message": "Invalid response format from MF API",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

        if "result" not in data:
            logger.error(f"MF API response missing 'result' field: {data}")
            return {
                "found": False,
                "nip": nip,
                "date": date,
                "message": "Missing result field in MF API response",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

        result = data["result"]

        if not result or "subject" not in result:
            logger.debug(f"MF API result structure: {result}")
            return {
                "found": False,
                "nip": nip,
                "date": date,
                "message": "No subject data found in MF response",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

        subject = result["subject"]

        try:
            # Extract bank accounts
            bank_accounts = []
            if "accountNumbers" in subject and isinstance(subject["accountNumbers"], list):
                for account in subject["accountNumbers"]:
                    bank_accounts.append({
                        "account_number": account,
                        "validated": True,
                        "date": date
                    })

            # Extract business address
            address = None
            if "workingAddress" in subject:
                addr_data = subject["workingAddress"]
                address = {
                    "street": addr_data.get("street", ""),
                    "building_number": addr_data.get("buildingNumber", ""),
                    "apartment_number": addr_data.get("apartmentNumber", ""),
                    "city": addr_data.get("city", ""),
                    "postal_code": addr_data.get("postalCode", ""),
                    "country": addr_data.get("country", "Polska")
                }

            # Extract residence address
            residence_address = None
            if "residenceAddress" in subject:
                addr_data = subject["residenceAddress"]
                residence_address = {
                    "street": addr_data.get("street", ""),
                    "building_number": addr_data.get("buildingNumber", ""),
                    "apartment_number": addr_data.get("apartmentNumber", ""),
                    "city": addr_data.get("city", ""),
                    "postal_code": addr_data.get("postalCode", ""),
                    "country": addr_data.get("country", "Polska")
                }

            # Extract representatives
            representatives = []
            if "representatives" in subject and isinstance(subject["representatives"], list):
                for rep in subject["representatives"]:
                    representatives.append({
                        "company_name": rep.get("companyName", ""),
                        "first_name": rep.get("firstName", ""),
                        "last_name": rep.get("lastName", ""),
                        "nip": rep.get("nip", ""),
                        "pesel": rep.get("pesel", "")
                    })

            # Extract authorized persons
            authorized_persons = []
            if "authorizedClerks" in subject and isinstance(subject["authorizedClerks"], list):
                for person in subject["authorizedClerks"]:
                    authorized_persons.append({
                        "company_name": person.get("companyName", ""),
                        "first_name": person.get("firstName", ""),
                        "last_name": person.get("lastName", ""),
                        "nip": person.get("nip", ""),
                        "pesel": person.get("pesel", "")
                    })

            # Extract business partners
            partners = []
            if "partners" in subject and isinstance(subject["partners"], list):
                for partner in subject["partners"]:
                    partners.append({
                        "company_name": partner.get("companyName", ""),
                        "first_name": partner.get("firstName", ""),
                        "last_name": partner.get("lastName", ""),
                        "nip": partner.get("nip", ""),
                        "pesel": partner.get("pesel", "")
                    })

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
                "address": address,
                "residence_address": residence_address,
                "bank_accounts": bank_accounts,
                "representatives": representatives,
                "authorized_persons": authorized_persons,
                "partners": partners,
                "has_virtual_accounts": subject.get("hasVirtualAccounts", False),
                "request_id": data.get("requestId", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error parsing MF response: {str(e)}")
            return {
                "found": False,
                "nip": nip,
                "date": date,
                "message": f"Error parsing MF response: {str(e)}",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
