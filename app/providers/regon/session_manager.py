"""Session manager for REGON API."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from .soap_client import RegonSoapClient

logger = logging.getLogger(__name__)


class RegonSessionManager:
    """Manages REGON API sessions."""

    def __init__(self, soap_client: RegonSoapClient, api_key: str):
        self.soap_client = soap_client
        self.api_key = api_key
        self.session_id: Optional[str] = None
        self.session_expires: Optional[datetime] = None

    async def get_session(self) -> str:
        """Get or create a session ID."""
        if (
            self.session_id
            and self.session_expires
            and datetime.now() < self.session_expires
        ):
            return self.session_id

        await self._create_session()
        if not self.session_id:
            raise RuntimeError("Failed to obtain session ID")
        return self.session_id

    async def _create_session(self):
        """Create a new session with REGON API."""
        logger.info("Creating REGON session")

        if not self.api_key:
            raise ValueError("REGON API key not configured")

        soap_body = self._build_login_soap_body()

        try:
            response_text = await self.soap_client.send_soap_request(
                soap_body=soap_body,
                action="http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj"
            )

            self._parse_session_response(response_text)

        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise

    def _build_login_soap_body(self) -> str:
        """Build SOAP body for login request."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:To>{self.soap_client.api_url}</wsa:To>
                <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj</wsa:Action>
            </soap:Header>
            <soap:Body>
                <ns:Zaloguj>
                    <ns:pKluczUzytkownika>{self.api_key}</ns:pKluczUzytkownika>
                </ns:Zaloguj>
            </soap:Body>
        </soap:Envelope>"""

    def _parse_session_response(self, response_text: str):
        """Parse session creation response."""
        namespaces = {
            'soap': 'http://www.w3.org/2003/05/soap-envelope',
            'ns': 'http://CIS/BIR/PUBL/2014/07'
        }

        root = self.soap_client.parse_xml_response(response_text, namespaces)

        result_element = self.soap_client.find_xml_element(
            root, './/ns:ZalogujResult', namespaces
        )

        if result_element is not None and result_element.text:
            self.session_id = result_element.text.strip()
            self.session_expires = datetime.now() + timedelta(minutes=30)
            logger.info(f"Session created successfully: {self.session_id[:20]}...")
        else:
            raise RuntimeError("Empty session ID received from REGON API")

    def is_session_valid(self) -> bool:
        """Check if current session is still valid."""
        return (
            self.session_id is not None
            and self.session_expires is not None
            and datetime.now() < self.session_expires
        )

    def invalidate_session(self):
        """Invalidate current session."""
        self.session_id = None
        self.session_expires = None
