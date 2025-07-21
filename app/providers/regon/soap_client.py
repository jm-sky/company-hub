"""SOAP client utilities for REGON API."""

import httpx
import xml.etree.ElementTree as ET
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RegonSoapClient:
    """SOAP client for REGON API operations."""

    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url
        self.timeout = timeout

    async def send_soap_request(
        self,
        soap_body: str,
        action: str,
        session_id: Optional[str] = None
    ) -> str:
        """Send a SOAP request to the REGON API."""
        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "Accept": "application/soap+xml",
        }

        if session_id:
            headers["sid"] = session_id

        logger.debug(f"Sending SOAP request to {self.api_url}")
        logger.debug(f"- Action: {action}")
        logger.debug(f"- Headers: {headers}")
        logger.debug(f"- Body: {soap_body[:200]}...")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.api_url, content=soap_body, headers=headers)

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response content: {response.text[:500]}...")

            if response.status_code != 200:
                raise httpx.HTTPStatusError(
                    f"SOAP request failed with status {response.status_code}",
                    request=response.request,
                    response=response
                )

            return response.text

    def extract_soap_envelope(self, response_text: str) -> str:
        """Extract the SOAP envelope from the response text."""
        pattern = r"(<s:Envelope.*?</s:Envelope>)"
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return response_text

    def parse_xml_response(self, xml_text: str, namespaces: Dict[str, str]) -> ET.Element:
        """Parse XML response and return root element."""
        try:
            cleaned_xml = self.extract_soap_envelope(xml_text)
            return ET.fromstring(cleaned_xml)
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML response: {str(e)}")
            logger.error(f"XML content: {xml_text[:1000]}...")
            raise

    def find_xml_element(
        self,
        root: ET.Element,
        xpath: str,
        namespaces: Dict[str, str]
    ) -> Optional[ET.Element]:
        """Find XML element using XPath with namespaces."""
        return root.find(xpath, namespaces)
