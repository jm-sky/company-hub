import httpx
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
        return self.session_id or ""


    async def _create_session(self):
        """Create a new session with REGON API."""
        if not self.api_key or self.api_key == "your-regon-api-key":
            raise ProviderError("REGON API key not configured", self.name)

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header/>
            <soap:Body>
                <ns:Zaloguj>
                    <ns:pKluczUzytkownika>{self.api_key}</ns:pKluczUzytkownika>
                </ns:Zaloguj>
            </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, data=soap_body, headers=headers)

            if response.status_code != 200:
                raise ProviderError(
                    f"Failed to create session: {response.status_code}. Response: {response.text[:200]}", self.name
                )

            # Parse session ID from response (simplified)
            # In production, you'd use proper XML parsing
            response_text = response.text
            if "ZalogujResult" in response_text:
                # Extract session ID from XML response
                # This is a simplified extraction - use proper XML parsing in production
                start = response_text.find("<ZalogujResult>") + len("<ZalogujResult>")
                end = response_text.find("</ZalogujResult>")
                self.session_id = response_text[start:end]
                self.session_expires = datetime.now() + timedelta(
                    minutes=30
                )  # Sessions expire after 30 minutes
            else:
                raise ProviderError(
                    "Failed to extract session ID from response", self.name
                )


    async def _search_company(self, nip: str) -> Dict[str, Any]:
        """Search for company by NIP to get basic info and entity type."""
        session_id = await self._get_session()

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header/>
            <soap:Body>
                <ns:DaneSzukajPodmioty>
                    <ns:pParametryWyszukiwania>
                        <ns:Nip>{nip}</ns:Nip>
                    </ns:pParametryWyszukiwania>
                </ns:DaneSzukajPodmioty>
            </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty",
            "sid": session_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, data=soap_body, headers=headers)

            if response.status_code != 200:
                raise ProviderError(
                    f"Search request failed: {response.status_code}", self.name
                )

            # Parse response (simplified)
            # In production, use proper XML parsing
            response_text = response.text
            if "DaneSzukajPodmiotyResult" in response_text:
                # Extract and parse the search result
                # This is a simplified parsing - use proper XML parsing in production
                return {"raw_response": response_text, "found": True}
            else:
                return {"raw_response": response_text, "found": False}


    async def _get_detailed_report(
        self, regon: str, entity_type: EntityType
    ) -> Dict[str, Any]:
        """Get detailed report for a company."""
        session_id = await self._get_session()
        report_name = self.entity_report_mapping[entity_type]

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header/>
            <soap:Body>
                <ns:DanePobierzPelnyRaport>
                    <ns:pRegon>{regon}</ns:pRegon>
                    <ns:pNazwaRaportu>{report_name.value}</ns:pNazwaRaportu>
                </ns:DanePobierzPelnyRaport>
            </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DanePobierzPelnyRaport",
            "sid": session_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, data=soap_body, headers=headers)

            if response.status_code != 200:
                raise ProviderError(
                    f"Detailed report request failed: {response.status_code}", self.name
                )

            # Parse response (simplified)
            response_text = response.text
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
        if not self.validate_identifier(nip):
            raise ValidationError(f"Invalid NIP format: {nip}", self.name)

        if self.is_rate_limited():
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
                    "message": "Company not found in REGON database",
                }

            # Step 2: Extract entity type and REGON from search result
            # In production, properly parse XML to extract these values
            # For now, we'll assume we found a legal person
            entity_type = (
                EntityType.LegalPerson
            )  # This should be parsed from search result
            regon = "123456789"  # This should be extracted from search result

            # Step 3: Get detailed report
            detailed_data = await self._get_detailed_report(regon, entity_type)

            return {
                "found": True,
                "nip": nip,
                "regon": regon,
                "entity_type": entity_type.value,
                "report_type": detailed_data["report_type"],
                "search_result": search_result,
                "detailed_data": detailed_data,
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
