"""Inbound API rate limiting, backed by Redis via slowapi/limits."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=[f"{settings.rate_limit_premium_tier}/hour"],
)

# Anonymous callers to the open company-lookup endpoint get the stricter
# free-tier limit, since each miss triggers real outbound calls to
# REGON/MF/IBAN.
anonymous_company_lookup_limit = f"{settings.rate_limit_free_tier}/hour"
