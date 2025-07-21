from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class ProviderConfig(BaseModel):
    """Configuration for a data provider."""
    name: str
    enabled: bool
    display_name: str
    description: str
    icon: str
    

class AppConfig(BaseModel):
    """Application configuration for frontend."""
    app_name: str
    app_version: str
    providers: List[ProviderConfig]
    rate_limits: dict
    features: dict


@router.get("/", response_model=AppConfig)
async def get_config():
    """Get application configuration."""
    return AppConfig(
        app_name="CompanyHub",
        app_version="1.0.0",
        providers=[
            ProviderConfig(
                name="regon",
                enabled=True,
                display_name="REGON",
                description="Oficjalne dane z rejestru działalności gospodarczej",
                icon="Building"
            ),
            ProviderConfig(
                name="mf",
                enabled=True,
                display_name="MF (Biała Lista)",
                description="Informacje o podatniku VAT z białej listy",
                icon="ShieldCheck"
            ),
            ProviderConfig(
                name="vies",
                enabled=False,
                display_name="VIES",
                description="Walidacja VAT w systemie VIES UE",
                icon="Globe"
            )
        ],
        rate_limits={
            "regon": "1 request per 5 seconds",
            "mf": "1 request per second",
            "vies": "1 request per second"
        },
        features={
            "company_search": True,
            "data_refresh": True,
            "export_data": False,
            "webhooks": False,
            "api_keys": False
        }
    )