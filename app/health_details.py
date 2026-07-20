"""Detailed health check for Ops Monitor.

Implements the response contract from ops-monitor's ``docs/health-schema.md``:
``GET /api/health/details`` reports per-component status plus a top-level
status that is the worst of all components. Protected by a static bearer token
(``HEALTH_DETAILS_TOKEN``).
"""

import asyncio
import secrets
from typing import Literal

import httpx
import redis
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text

from app.config import settings
from app.db.database import engine

ComponentStatus = Literal["ok", "degraded", "failed"]

_CHECK_TIMEOUT_SECONDS = 3.0
_STATUS_SEVERITY: dict[ComponentStatus, int] = {"ok": 0, "degraded": 1, "failed": 2}

_health_details_security = HTTPBearer(auto_error=False)


async def verify_health_details_token(
    credentials: HTTPAuthorizationCredentials | None = Security(_health_details_security),
) -> None:
    """Require a valid ``Authorization: Bearer <token>`` header."""
    expected = settings.health_details_token
    if not expected or not credentials or not secrets.compare_digest(credentials.credentials, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing health details token",
        )


def _check_database() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}


def _check_cache() -> dict:
    try:
        client = redis.from_url(
            settings.redis_url,
            socket_connect_timeout=_CHECK_TIMEOUT_SECONDS,
            socket_timeout=_CHECK_TIMEOUT_SECONDS,
        )
        client.ping()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}


async def _check_frontend() -> dict:
    url = settings.frontend_url
    if not url:
        return {"status": "ok"}

    try:
        async with httpx.AsyncClient(timeout=_CHECK_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
        if response.status_code == 200:
            return {"status": "ok"}
        return {
            "status": "failed",
            "reason": f"HTTP {response.status_code} from frontend origin",
        }
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}


def _check_regon() -> dict:
    if settings.regon_api_key:
        return {"status": "ok"}
    return {
        "status": "degraded",
        "reason": "REGON API key not configured",
    }


def _check_iban() -> dict:
    if settings.iban_api_key or settings.ibanapi_com_key:
        return {"status": "ok"}
    return {
        "status": "degraded",
        "reason": "No IBAN enrichment API key configured",
    }


def _worst_status(statuses: list[ComponentStatus]) -> ComponentStatus:
    return max(statuses, key=lambda s: _STATUS_SEVERITY[s], default="ok")


async def build_health_details() -> dict:
    """Run component checks concurrently and assemble the response."""
    database, cache, regon, iban = await asyncio.gather(
        asyncio.to_thread(_check_database),
        asyncio.to_thread(_check_cache),
        asyncio.to_thread(_check_regon),
        asyncio.to_thread(_check_iban),
    )
    frontend = await _check_frontend()

    components = {
        "database": database,
        "cache": cache,
        "frontend": frontend,
        "regon": regon,
        "iban": iban,
    }

    component_statuses = [c["status"] for c in components.values()]
    overall = _worst_status(component_statuses)

    errors = [
        f"{name}: {component['reason']}"
        for name, component in components.items()
        if component.get("reason") and component["status"] != "ok"
    ]

    return {
        "schema_version": 1,
        "status": overall,
        "version": settings.app_version,
        "environment": settings.environment,
        "components": components,
        "errors": errors or None,
        "meta": {
            "regon_configured": bool(settings.regon_api_key),
            "iban_configured": bool(settings.iban_api_key or settings.ibanapi_com_key),
        },
    }
