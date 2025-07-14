from fastapi import FastAPI
from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(
    title="CompanyHub API",
    description="Centralized API service for Polish company data aggregation",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "CompanyHub API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
