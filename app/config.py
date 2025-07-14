from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/companyhub"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "your-secret-key-change-this"
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

    # Cache TTL (in seconds)
    cache_ttl_default: int = 86400  # 1 day
    cache_ttl_bank_accounts: int = 604800  # 7 days

    # Rate limiting
    rate_limit_free_tier: int = 5  # requests per hour
    rate_limit_premium_tier: int = 1000  # requests per hour

    class Config:
        env_file = ".env"


settings = Settings()
