from fastapi import APIRouter, Depends

from app.health_details import build_health_details, verify_health_details_token

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health/details",
    dependencies=[Depends(verify_health_details_token)],
)
async def health_check_details() -> dict:
    """Detailed health check for Ops Monitor (bearer-token protected)."""
    return await build_health_details()
