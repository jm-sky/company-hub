import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import settings
from app.exception_handlers import http_exception_handler

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set specific loggers to DEBUG for more detailed output
# logging.getLogger("app.providers.regon").setLevel(logging.DEBUG)
logging.getLogger("app.providers.iban").setLevel(logging.DEBUG)
logging.getLogger("app.providers.mf").setLevel(logging.DEBUG)

app = FastAPI(
    title="CompanyHub API",
    description="Centralized API service for Polish company data aggregation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods.split(","),
    allow_headers=settings.cors_allow_headers.split(",") if settings.cors_allow_headers != "*" else ["*"],
)

# Add HTTP exception handler to ensure CORS headers are included
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "CompanyHub API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
