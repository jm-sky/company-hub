from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
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
from app.db.database import get_db
from app.db.models import Company, RegonData
from app.crud.companies import (
    get_or_create_company,
    get_regon_data,
    is_regon_data_expired,
    store_regon_data,
)

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
    db: Session = Depends(get_db),
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

    # Get or create company record
    company: Company = get_or_create_company(db, normalized_nip)

    # Initialize response data
    response_data = CompanyDataResponse(nip=normalized_nip)
    response_metadata = CompanyMetadataResponse()

    # Track if any provider is rate limited
    any_rate_limited = False

    # Handle REGON data
    should_fetch_regon = "regon" in refresh_providers if refresh else False
    cached_regon_data: RegonData | None = get_regon_data(db, company.id)  # type: ignore

    if not should_fetch_regon and cached_regon_data and not is_regon_data_expired(cached_regon_data):
        # Use cached data
        response_data.regon = cached_regon_data.data  # type: ignore
        response_metadata.regon = ProviderMetadata(
            status="cached", fetched_at=cached_regon_data.fetched_at.isoformat()
        )
    else:
        # Fetch fresh data
        regon_provider = RegonProvider()
        try:
            regon_data = await regon_provider.fetch_data(normalized_nip)
            response_data.regon = regon_data
            response_metadata.regon = ProviderMetadata(
                status="fresh", fetched_at=regon_data.get("fetched_at")
            )

            # Store in database
            if "entity_type" in regon_data and "report_type" in regon_data:
                store_regon_data(
                    db,
                    company.id,  # type: ignore
                    regon_data["entity_type"],
                    regon_data["report_type"],
                    regon_data
                )

                # Update company name if available
                if "name" in regon_data and regon_data["name"] != company.name:
                    company.name = regon_data["name"]  # type: ignore
                    db.commit()

        except RateLimitError as e:
            any_rate_limited = True
            response_metadata.regon = ProviderMetadata(
                status="rate_limited", next_available_at=e.retry_after
            )
            # Use cached data if available
            if cached_regon_data:
                response_data.regon = cached_regon_data.data  # type: ignore
                response_metadata.regon.status = "cached_due_to_rate_limit"  # type: ignore
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
        raise HTTPException(status_code=429, detail=error_response.model_dump())

    # Return success response
    return SuccessResponse(data=response_data, metadata=response_metadata)


@router.get("/", response_model=List[str])
async def list_companies():
    """List available companies (placeholder)."""
    return ["This endpoint will list companies when implemented"]
