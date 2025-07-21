from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/companyhub"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # REGON API
    regon_api_url: str = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
    regon_api_key: str = ""

    # MF API
    mf_api_url: str = "https://wl-api.mf.gov.pl"

    # VIES API
    vies_api_url: str = "http://ec.europa.eu/taxation_customs/vies/services/checkVatService"

    # IBAN API
    iban_api_url: str = "https://api.iban.com/clients/api"
    iban_api_key: str = ""

    # IbanApi.com (different service)
    ibanapi_com_key: str = ""

    # APILayer Bank Data API
    apilayer_api_key: str = ""

    # Cache TTL (in seconds)
    cache_ttl_default: int = 86400  # 1 day
    cache_ttl_bank_accounts: int = 604800  # 7 days

    # Rate limiting
    rate_limit_free_tier: int = 5  # requests per hour
    rate_limit_premium_tier: int = 1000  # requests per hour

    # CORS settings
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: str = "*"

    # Admin user settings
    admin_name: str = "Admin"
    admin_email: str = "admin@companyhub.local"
    admin_password: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
