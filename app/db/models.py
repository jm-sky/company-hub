from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)  # Made nullable for OAuth users
    plan = Column(String(20), default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active = Column(Boolean, default=True)
    
    # OAuth provider fields
    github_id = Column(String(50), unique=True, nullable=True, index=True)
    github_username = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    google_email = Column(String(255), nullable=True)
    
    # Shared OAuth fields
    avatar_url = Column(String(500), nullable=True)
    oauth_provider = Column(String(50), nullable=True)  # 'github', 'google', etc.
    oauth_access_token = Column(Text, nullable=True)  # Encrypted storage
    oauth_refresh_token = Column(Text, nullable=True)  # Encrypted storage

    # Relationships
    api_tokens = relationship("ApiToken", back_populates="user")
    subscriptions = relationship("UserCompanySubscription", back_populates="user")
    callbacks = relationship("CallbackQueue", back_populates="user")
    usage_logs = relationship("ApiUsage", back_populates="user")


class ApiToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_name = Column(String(100), nullable=False)
    token_hash = Column(String(255), nullable=False)
    permissions = Column(JSONB, default={})
    rate_limit_per_hour = Column(Integer, default=5)
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="api_tokens")
    usage_logs = relationship("ApiUsage", back_populates="token")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    nip = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    regon_data = relationship("RegonData", back_populates="company")
    mf_data = relationship("MfData", back_populates="company")
    vies_data = relationship("ViesData", back_populates="company")
    bank_accounts = relationship("CompanyBankAccount", back_populates="company")
    subscriptions = relationship("UserCompanySubscription", back_populates="company")
    data_changes = relationship("DataChange", back_populates="company")


class RegonData(Base):
    __tablename__ = "regon_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    entity_type = Column(String(2), nullable=False)  # P, F, LP, LF
    report_type = Column(String(50), nullable=False)  # BIR11OsPrawna, etc.
    data = Column(JSONB, nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(
        DateTime(timezone=True), server_default=func.now() + func.interval("1 day")
    )

    # Relationships
    company = relationship("Company", back_populates="regon_data")

    __table_args__ = ({"sqlite_autoincrement": True},)


class MfData(Base):
    __tablename__ = "mf_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    data = Column(JSONB, nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(
        DateTime(timezone=True), server_default=func.now() + func.interval("1 day")
    )

    # Relationships
    company = relationship("Company", back_populates="mf_data")


class ViesData(Base):
    __tablename__ = "vies_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    data = Column(JSONB, nullable=False)
    consultation_number = Column(String(100))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(
        DateTime(timezone=True), server_default=func.now() + func.interval("1 day")
    )

    # Relationships
    company = relationship("Company", back_populates="vies_data")


class CompanyBankAccount(Base):
    __tablename__ = "company_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    account_number = Column(String(50), nullable=False)
    source = Column(String(20), nullable=False)  # 'mf', 'manual', etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company", back_populates="bank_accounts")
    iban_enrichment = relationship("IbanEnrichment", back_populates="account")


class IbanEnrichment(Base):
    __tablename__ = "iban_enrichment"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(
        Integer,
        ForeignKey("company_bank_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    bank_name = Column(String(255))
    bank_code = Column(String(20))
    country_code = Column(String(2))
    currency = Column(String(3))
    is_valid = Column(Boolean)
    validation_message = Column(Text)
    enrichment_data = Column(JSONB)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(
        DateTime(timezone=True), server_default=func.now() + func.interval("7 days")
    )

    # Relationships
    account = relationship("CompanyBankAccount", back_populates="iban_enrichment")


class UserCompanySubscription(Base):
    __tablename__ = "user_company_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    webhook_url = Column(Text, nullable=False)
    providers = Column(ARRAY(String), nullable=False)  # ['regon', 'mf', 'vies']
    validation_schedule = Column(
        String(20), nullable=False
    )  # daily, weekly, monthly, custom
    custom_interval_hours = Column(Integer)
    last_validated_at = Column(DateTime(timezone=True))
    next_validation_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscriptions")


class CallbackQueue(Base):
    __tablename__ = "callback_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_nip = Column(String(10), nullable=False)
    providers = Column(ARRAY(String), nullable=False)  # ['regon', 'mf', 'vies']
    webhook_url = Column(Text, nullable=False)
    trigger_type = Column(
        String(20), nullable=False
    )  # scheduled, opportunistic, on_demand
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True))
    status = Column(
        String(20), default="pending"
    )  # pending, processing, completed, failed
    error_message = Column(Text)

    # Relationships
    user = relationship("User", back_populates="callbacks")
    deliveries = relationship("WebhookDelivery", back_populates="callback")


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    callback_id = Column(
        Integer, ForeignKey("callback_queue.id", ondelete="CASCADE"), nullable=False
    )
    attempt_number = Column(Integer, nullable=False)
    http_status = Column(Integer)
    response_body = Column(Text)
    response_headers = Column(JSONB)
    delivered_at = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, nullable=False)

    # Relationships
    callback = relationship("CallbackQueue", back_populates="deliveries")


class ApiUsage(Base):
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_id = Column(
        Integer, ForeignKey("api_tokens.id", ondelete="CASCADE"), nullable=False
    )
    company_nip = Column(String(10))
    endpoint = Column(String(100), nullable=False)
    providers_requested = Column(ARRAY(String))
    providers_fresh = Column(ARRAY(String))
    providers_cached = Column(ARRAY(String))
    providers_rate_limited = Column(ARRAY(String))
    response_status = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="usage_logs")
    token = relationship("ApiToken", back_populates="usage_logs")


class DataChange(Base):
    __tablename__ = "data_changes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(String(20), nullable=False)  # regon, mf, vies, iban
    change_type = Column(String(20), nullable=False)  # created, updated, deleted
    field_changes = Column(JSONB)
    old_data = Column(JSONB)
    new_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="data_changes")
