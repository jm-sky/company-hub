from fastapi import APIRouter
from app.api.v1.endpoints import companies
from app.api.v1.endpoints import auth

api_router = APIRouter()
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
