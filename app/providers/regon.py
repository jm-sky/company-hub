import httpx
import xml.etree.ElementTree as ET
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum
from app.providers.base import (
    BaseProvider,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from app.utils.validators import validate_nip
from app.config import settings

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


class RegonProvider(BaseProvider):
    """REGON API provider implementation."""

    # Rate limiting configuration based on REGON API limits
    RATE_LIMITS = {
        "peak": {"per_second": 3, "per_minute": 120, "per_hour": 6000},  # 8:00-16:59
        "off_peak_1": {  # 6:00-7:59, 17:00-21:59
            "per_second": 3,
            "per_minute": 150,
            "per_hour": 8000,
        },
        "off_peak_2": {  # 22:00-5:59
            "per_second": 4,
            "per_minute": 200,
            "per_hour": 10000,
        },
    }

    def __init__(self):
        super().__init__("regon")
        self.api_url = settings.regon_api_url
        self.api_key = settings.regon_api_key
        self.session_id: Optional[str] = None
        self.session_expires: Optional[datetime] = None
        self.request_count = 0
        self.last_request_time: Optional[datetime] = None

        # Entity type to report mapping
        self.entity_report_mapping = {
            EntityType.LegalPerson: RegonReportName.BIR11LegalPerson,
            EntityType.NaturalPerson: RegonReportName.BIR11NaturalPersonCeidg,
            EntityType.LocalLegalPersonUnit: RegonReportName.BIR11LocalLegalPersonUnit,
            EntityType.LocalNaturalPersonUnit: RegonReportName.BIR11LocalNaturalPersonUnit,
        }


    def validate_identifier(self, identifier: str) -> bool:
        """Validate NIP format."""
        return validate_nip(identifier)


    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if not self.last_request_time:
            return False

        now = datetime.now()
        time_since_last = now - self.last_request_time

        # Get current rate limits based on time of day
        current_limits = self._get_current_rate_limits()

        # Check if we need to wait (simplified check for per-second limit)
        return time_since_last.total_seconds() < (1 / current_limits["per_second"])


    def get_next_available_time(self) -> Optional[datetime]:
        """Get next available time for requests."""
        if not self.is_rate_limited():
            return None

        current_limits = self._get_current_rate_limits()
        wait_time = 1 / current_limits["per_second"]

        if self.last_request_time:
            return self.last_request_time + timedelta(seconds=wait_time)

        return None


    def _get_current_rate_limits(self) -> Dict[str, int]:
        """Get current rate limits based on time of day."""
        now = datetime.now()
        hour = now.hour

        if 8 <= hour <= 16:
            return self.RATE_LIMITS["peak"]
        elif (6 <= hour <= 7) or (17 <= hour <= 21):
            return self.RATE_LIMITS["off_peak_1"]
        else:
            return self.RATE_LIMITS["off_peak_2"]


    async def _get_session(self) -> str:
        """Get or create a session ID."""
        if (
            self.session_id
            and self.session_expires
            and datetime.now() < self.session_expires
        ):
            return self.session_id

        await self._create_session()
        if not self.session_id:
            raise ProviderError("Failed to obtain session ID", self.name)
        return self.session_id


    async def _create_session(self):
        """Create a new session with REGON API."""
        logger.info(f"Creating REGON session with API URL: {self.api_url}")

        if not self.api_key:
            logger.error("REGON API key not configured")
            raise ProviderError("REGON API key not configured", self.name)

        logger.debug(f"Using API key: {self.api_key[:10]}...")  # Show first 10 chars for debugging

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:To>{self.api_url}</wsa:To>
                <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj</wsa:Action>
            </soap:Header>
            <soap:Body>
                <ns:Zaloguj>
                    <ns:pKluczUzytkownika>{self.api_key}</ns:pKluczUzytkownika>
                </ns:Zaloguj>
            </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "Accept": "application/soap+xml",
        }

        async with httpx.AsyncClient() as client:
            logger.debug(f"Sending SOAP request to {self.api_url}")
            logger.debug(f"Request headers: {headers}")
            logger.debug(f"Request body: {soap_body[:200]}...")

            response = await client.post(self.api_url, content=soap_body, headers=headers)

            logger.info(f"Session creation response: {response.status_code}")
            logger.debug(f"Response content: {response.text[:500]}...")

            if response.status_code != 200:
                logger.error(f"Session creation failed: {response.status_code}")
                raise ProviderError(
                    f"Failed to create session: {response.status_code}. Response: {response.text[:200]}", self.name
                )

            response_text = self._extractSoapEnvelope(response.text)

            # Parse session ID from response using proper XML parsing
            try:
                root = ET.fromstring(response_text)

                # Find the ZalogujResult element
                namespaces = {
                    'soap': 'http://www.w3.org/2003/05/soap-envelope',
                    'ns': 'http://CIS/BIR/PUBL/2014/07'
                }

                result_element = root.find('.//ns:ZalogujResult', namespaces)
                if result_element is not None and result_element.text:
                    self.session_id = result_element.text.strip()
                    self.session_expires = datetime.now() + timedelta(minutes=30)
                    logger.info(f"Session created successfully: {self.session_id[:20]}...")
                else:
                    logger.error("Empty session ID received")
                    raise ProviderError(
                        "Empty session ID received from REGON API", self.name
                    )
            except ET.ParseError as e:
                logger.error(f"Failed to parse XML response: {str(e)}")
                raise ProviderError(f"Failed to parse XML response: {str(e)}", self.name)
            except Exception as e:
                logger.error(f"Error extracting session ID: {str(e)}")
                raise ProviderError(f"Error extracting session ID: {str(e)}", self.name)


    async def _search_company(self, nip: str) -> Dict[str, Any]:
        """Search for company by NIP to get basic info and entity type."""
        session_id = await self._get_session()

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07" xmlns:dat="http://CIS/BIR/PUBL/2014/07/DataContract">
            <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty</wsa:Action>
                <wsa:To>{self.api_url}</wsa:To>
            </soap:Header>
            <soap:Body>
                <ns:DaneSzukajPodmioty>
                    <ns:pParametryWyszukiwania>
                        <dat:Nip>{nip}</dat:Nip>
                    </ns:pParametryWyszukiwania>
                </ns:DaneSzukajPodmioty>
            </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "Accept": "application/soap+xml",
            "sid": session_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, content=soap_body, headers=headers)

            if response.status_code != 200:
                logger.error(f"Search request failed: {response.status_code}")
                raise ProviderError(
                    f"Search request failed: {response.status_code}", self.name
                )

            # Parse response using proper XML parsing
            try:
                response_text = self._extractSoapEnvelope(response.text)

                root = ET.fromstring(response_text)

                namespaces = {
                    'soap': 'http://www.w3.org/2003/05/soap-envelope',
                    'ns': 'http://CIS/BIR/PUBL/2014/07'
                }

                result_element = root.find('.//ns:DaneSzukajPodmiotyResult', namespaces)
                if result_element is not None and result_element.text:
                    result_data = result_element.text.strip()
                    if result_data:
                        # Parse the inner XML data
                        try:
                            inner_root = ET.fromstring(result_data)
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
                            return {"found": True, "raw_data": result_data}
                    else:
                        return {"found": False, "message": "Empty search result"}
                else:
                    return {"found": False, "message": "No search result element found"}
            except ET.ParseError as e:
                logger.error(f"Failed to parse search response: {str(e)}")
                raise ProviderError(f"Failed to parse search response: {str(e)}", self.name)
            except Exception as e:
                logger.error(f"Error parsing search response: {str(e)}")
                raise ProviderError(f"Error parsing search response: {str(e)}", self.name)


    async def _get_detailed_report(
        self, regon: str, entity_type: EntityType
    ) -> Dict[str, Any]:
        """Get detailed report for a company."""
        session_id = await self._get_session()
        report_name = self.entity_report_mapping[entity_type]

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DanePobierzPelnyRaport</wsa:Action>
                <wsa:To>{self.api_url}</wsa:To>
            </soap:Header>
            <soap:Body>
                <ns:DanePobierzPelnyRaport>
                    <ns:pRegon>{regon}</ns:pRegon>
                    <ns:pNazwaRaportu>{report_name.value}</ns:pNazwaRaportu>
                </ns:DanePobierzPelnyRaport>
            </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "Accept": "application/soap+xml",
            "sid": session_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, content=soap_body, headers=headers)

            if response.status_code != 200:
                raise ProviderError(
                    f"Detailed report request failed: {response.status_code}", self.name
                )

            # Parse response (simplified)
            response_text = self._extractSoapEnvelope(response.text)

            if "DanePobierzPelnyRaportResult" in response_text:
                return {"raw_response": response_text, "report_type": report_name.value}
            else:
                raise ProviderError("Failed to get detailed report", self.name)


    async def fetch_data(self, nip: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch company data from REGON API.

        This is a two-step process:
        1. Search by NIP to get basic info and determine entity type
        2. Get detailed report based on entity type
        """
        logger.info(f"Fetching data for NIP: {nip}")

        if not self.validate_identifier(nip):
            logger.error(f"Invalid NIP format: {nip}")
            raise ValidationError(f"Invalid NIP format: {nip}", self.name)

        if self.is_rate_limited():
            logger.warning(f"Rate limited for NIP: {nip}")
            raise RateLimitError(self.name, self.get_next_available_time())

        try:
            # Update request tracking
            self.last_request_time = datetime.now()
            self.request_count += 1

            # Step 1: Search for company
            search_result = await self._search_company(nip)

            if not search_result["found"]:
                return {
                    "found": False,
                    "nip": nip,
                    "message": search_result.get("message", "Company not found in REGON database"),
                    "fetched_at": datetime.now().isoformat(),
                }

            # Step 2: Extract entity type and REGON from search result
            if "data" in search_result:
                company_data = search_result["data"]
                regon = company_data.get("Regon", "")
                typ = company_data.get("Typ", "")

                # Map the type to EntityType
                if typ == "P":
                    entity_type = EntityType.LegalPerson
                elif typ == "F":
                    entity_type = EntityType.NaturalPerson
                elif typ == "LP":
                    entity_type = EntityType.LocalLegalPersonUnit
                elif typ == "LF":
                    entity_type = EntityType.LocalNaturalPersonUnit
                else:
                    entity_type = EntityType.LegalPerson  # Default

                # Basic company info from search
                basic_info = {
                    "found": True,
                    "nip": nip,
                    "regon": regon,
                    "name": company_data.get("Nazwa", ""),
                    "entity_type": entity_type.value,
                    "search_result": search_result,
                    "fetched_at": datetime.now().isoformat(),
                }

                # Try to get detailed report if we have REGON
                if regon:
                    try:
                        detailed_data = await self._get_detailed_report(regon, entity_type)
                        basic_info["detailed_data"] = detailed_data
                        basic_info["report_type"] = detailed_data.get("report_type", "")
                    except Exception as e:
                        # If detailed report fails, still return basic info
                        basic_info["detailed_error"] = str(e)

                return basic_info
            else:
                # Return basic found info even if we can't parse the data
                return {
                    "found": True,
                    "nip": nip,
                    "message": "Company found but data parsing incomplete",
                    "raw_data": search_result.get("raw_data", ""),
                    "fetched_at": datetime.now().isoformat(),
                }

        except httpx.TimeoutException:
            raise ProviderError("Request timeout", self.name, 408)
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"HTTP error: {e.response.status_code}",
                self.name,
                e.response.status_code,
            )
        except Exception as e:
            raise ProviderError(f"Unexpected error: {str(e)}", self.name)


    def _extractSoapEnvelope(self, response_text: str) -> str:
        """Extract the SOAP envelope from the response text."""
        pattern = r"(<s:Envelope.*?</s:Envelope>)"
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return response_text
