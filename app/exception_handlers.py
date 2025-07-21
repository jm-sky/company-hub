from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.config import settings


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler that ensures CORS headers are included
    in error responses.
    """
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("Origin", "*"),
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }

    # Only set origin header if it's in allowed origins
    origin = request.headers.get("Origin")
    allowed_origins = settings.cors_origins.split(",")
    if origin and origin in allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
    elif "*" in allowed_origins:
        headers["Access-Control-Allow-Origin"] = "*"
    else:
        headers["Access-Control-Allow-Origin"] = allowed_origins[0] if allowed_origins else "*"

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )