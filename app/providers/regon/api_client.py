"""REGON API client for specific operations."""

import logging
from typing import Dict, Any
from .soap_client import RegonSoapClient
from .session_manager import RegonSessionManager
from .data_mapper import RegonDataMapper, EntityType

logger = logging.getLogger(__name__)


class RegonApiClient:
    """Client for REGON API operations."""
    
    def __init__(self, soap_client: RegonSoapClient, session_manager: RegonSessionManager, data_mapper: RegonDataMapper):
        self.soap_client = soap_client
        self.session_manager = session_manager
        self.data_mapper = data_mapper
        
    async def search_company(self, nip: str) -> Dict[str, Any]:
        """Search for company by NIP to get basic info and entity type."""
        session_id = await self.session_manager.get_session()
        
        soap_body = self._build_search_soap_body(nip)
        
        try:
            response_text = await self.soap_client.send_soap_request(
                soap_body=soap_body,
                action="http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty",
                session_id=session_id
            )
            
            return self._parse_search_response(response_text)
            
        except Exception as e:
            logger.error(f"Search request failed: {str(e)}")
            raise
            
    async def get_detailed_report(self, regon: str, entity_type: EntityType) -> Dict[str, Any]:
        """Get detailed report for a company."""
        session_id = await self.session_manager.get_session()
        report_name = self.data_mapper.get_report_name(entity_type)
        
        soap_body = self._build_report_soap_body(regon, report_name.value)
        
        try:
            response_text = await self.soap_client.send_soap_request(
                soap_body=soap_body,
                action="http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DanePobierzPelnyRaport",
                session_id=session_id
            )
            
            return self._parse_report_response(response_text, report_name.value)
            
        except Exception as e:
            logger.error(f"Detailed report request failed: {str(e)}")
            raise
            
    def _build_search_soap_body(self, nip: str) -> str:
        """Build SOAP body for search request."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07" xmlns:dat="http://CIS/BIR/PUBL/2014/07/DataContract">
            <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty</wsa:Action>
                <wsa:To>{self.soap_client.api_url}</wsa:To>
            </soap:Header>
            <soap:Body>
                <ns:DaneSzukajPodmioty>
                    <ns:pParametryWyszukiwania>
                        <dat:Nip>{nip}</dat:Nip>
                    </ns:pParametryWyszukiwania>
                </ns:DaneSzukajPodmioty>
            </soap:Body>
        </soap:Envelope>"""
        
    def _build_report_soap_body(self, regon: str, report_name: str) -> str:
        """Build SOAP body for detailed report request."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
            <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DanePobierzPelnyRaport</wsa:Action>
                <wsa:To>{self.soap_client.api_url}</wsa:To>
            </soap:Header>
            <soap:Body>
                <ns:DanePobierzPelnyRaport>
                    <ns:pRegon>{regon}</ns:pRegon>
                    <ns:pNazwaRaportu>{report_name}</ns:pNazwaRaportu>
                </ns:DanePobierzPelnyRaport>
            </soap:Body>
        </soap:Envelope>"""
        
    def _parse_search_response(self, response_text: str) -> Dict[str, Any]:
        """Parse search response."""
        namespaces = {
            'soap': 'http://www.w3.org/2003/05/soap-envelope',
            'ns': 'http://CIS/BIR/PUBL/2014/07'
        }
        
        root = self.soap_client.parse_xml_response(response_text, namespaces)
        
        result_element = self.soap_client.find_xml_element(
            root, './/ns:DaneSzukajPodmiotyResult', namespaces
        )
        
        if result_element is not None and result_element.text:
            result_data = result_element.text.strip()
            if result_data:
                return self.data_mapper.parse_search_response(result_data)
            else:
                return {"found": False, "message": "Empty search result"}
        else:
            return {"found": False, "message": "No search result element found"}
            
    def _parse_report_response(self, response_text: str, report_type: str) -> Dict[str, Any]:
        """Parse detailed report response."""
        cleaned_response = self.soap_client.extract_soap_envelope(response_text)
        
        if "DanePobierzPelnyRaportResult" in cleaned_response:
            return self.data_mapper.extract_detailed_data(cleaned_response, report_type)
        else:
            raise RuntimeError("Failed to get detailed report")