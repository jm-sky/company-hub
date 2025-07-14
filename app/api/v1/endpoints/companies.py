from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.schemas.company import (
    SuccessResponse,
    ErrorResponse,
    CompanyDataResponse,
    CompanyMetadataResponse,
    ProviderMetadata,
)
from app.providers.regon import RegonProvider
from app.providers.base import RateLimitError, ValidationError, ProviderError
from app.utils.validators import normalize_nip

router = APIRouter()


@router.get("/{nip}", response_model=SuccessResponse)
async def get_company_data(
    nip: str,
    refresh: Optional[str] = Query(
        None, description="Comma-separated list of providers to refresh (regon,mf,vies)"
    ),
    partial: Optional[str] = Query(
        None,
        description="Set to 'allow' to return 200 with partial data instead of 429",
    ),
):
    """
    Get company data by NIP.

    - **nip**: Polish NIP (Tax Identification Number)
    - **refresh**: Optional comma-separated list of providers to refresh
    - **partial**: Set to 'allow' to get 200 status with partial data instead of 429
    """

    # Normalize and validate NIP
    normalized_nip = normalize_nip(nip)
    if not normalized_nip:
        raise HTTPException(status_code=400, detail="Invalid NIP format")

    # Parse refresh parameter
    refresh_providers = []
    if refresh:
        refresh_providers = [p.strip() for p in refresh.split(",")]

    # Initialize response data
    response_data = CompanyDataResponse(nip=normalized_nip)
    response_metadata = CompanyMetadataResponse()

    # Track if any provider is rate limited
    any_rate_limited = False

    # Fetch REGON data
    regon_provider = RegonProvider()
    try:
        regon_data = await regon_provider.fetch_data(normalized_nip)
        response_data.regon = regon_data
        response_metadata.regon = ProviderMetadata(
            status="fresh", fetched_at=regon_data.get("fetched_at")
        )
    except RateLimitError as e:
        any_rate_limited = True
        response_metadata.regon = ProviderMetadata(
            status="rate_limited", next_available_at=e.retry_after
        )
    except ValidationError as e:
        response_metadata.regon = ProviderMetadata(
            status="error", error_message=e.message
        )
    except ProviderError as e:
        response_metadata.regon = ProviderMetadata(
            status="error", error_message=e.message
        )

    # TODO: Add MF and VIES providers similarly

    # Determine response status
    if any_rate_limited and partial != "allow":
        # Return 429 with available data
        error_response = ErrorResponse(
            error="rate_limited",
            message="Some providers hit rate limits",
            data=response_data,
            metadata=response_metadata,
        )
        raise HTTPException(status_code=429, detail=error_response.dict())

    # Return success response
    return SuccessResponse(data=response_data, metadata=response_metadata)


@router.get("/", response_model=List[str])
async def list_companies():
    """List available companies (placeholder)."""
    return ["This endpoint will list companies when implemented"]
