from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import ApiResponse


class ProviderMetadata(BaseModel):
    """Metadata for individual provider data."""

    status: str  # cached, fresh, rate_limited, error
    cached_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    next_available_at: Optional[datetime] = None
    error_message: Optional[str] = None


class CompanyDataResponse(BaseModel):
    """Complete company data response."""

    nip: str
    regon: Optional[Dict[str, Any]] = None
    mf: Optional[Dict[str, Any]] = None
    vies: Optional[Dict[str, Any]] = None
    bank_accounts: Optional[List[Dict[str, Any]]] = None


class CompanyMetadataResponse(BaseModel):
    """Metadata for company data response."""

    regon: Optional[ProviderMetadata] = None
    mf: Optional[ProviderMetadata] = None
    vies: Optional[ProviderMetadata] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    data: Optional[CompanyDataResponse] = None
    metadata: Optional[CompanyMetadataResponse] = None


class SuccessResponse(BaseModel):
    """Success response schema."""

    data: CompanyDataResponse
    metadata: CompanyMetadataResponse


class CompanyResponse(BaseModel):
    """Response schema for company data."""

    data: CompanyDataResponse
    metadata: CompanyMetadataResponse

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CompanyApiResponse(ApiResponse):
    """API response wrapper for company data."""

    data: CompanyResponse
