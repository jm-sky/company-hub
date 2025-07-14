-- CompanyHub Database Schema
-- PostgreSQL

-- Users and authentication
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan VARCHAR(20) DEFAULT 'free', -- free, premium, enterprise
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- API tokens (JWT support)
CREATE TABLE api_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    token_name VARCHAR(100) NOT NULL,
    token_hash VARCHAR(255) NOT NULL, -- Hash of the actual token
    permissions JSONB DEFAULT '{}', -- Permissions object
    rate_limit_per_hour INTEGER DEFAULT 5, -- Based on user plan
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Main companies table
CREATE TABLE companies (
    id BIGSERIAL PRIMARY KEY,
    nip VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255), -- Basic company name from first successful fetch
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- REGON data storage
CREATE TABLE regon_data (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    entity_type VARCHAR(2) NOT NULL, -- P, F, LP, LF
    report_type VARCHAR(50) NOT NULL, -- BIR11OsPrawna, etc.
    data JSONB NOT NULL, -- Full report data
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    UNIQUE(company_id, entity_type, report_type)
);

-- MF (Biała Lista) data storage
CREATE TABLE mf_data (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    data JSONB NOT NULL, -- Full MF response data
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    UNIQUE(company_id)
);

-- VIES data storage
CREATE TABLE vies_data (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    data JSONB NOT NULL, -- Full VIES response data
    consultation_number VARCHAR(100), -- VIES consultation identifier
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    UNIQUE(company_id)
);

-- Company bank accounts (from MF data)
CREATE TABLE company_bank_accounts (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    account_number VARCHAR(50) NOT NULL, -- IBAN or domestic format
    source VARCHAR(20) NOT NULL, -- 'mf', 'manual', etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, account_number)
);

-- IBAN enrichment data for bank accounts
CREATE TABLE iban_enrichment (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES company_bank_accounts(id) ON DELETE CASCADE,
    bank_name VARCHAR(255),
    bank_code VARCHAR(20),
    country_code VARCHAR(2),
    currency VARCHAR(3),
    is_valid BOOLEAN,
    validation_message TEXT,
    enrichment_data JSONB, -- Full IBAN API response
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    UNIQUE(account_id)
);

-- User company subscriptions (which companies they want to monitor)
CREATE TABLE user_company_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    webhook_url TEXT NOT NULL,
    providers TEXT[] NOT NULL, -- ['regon', 'mf', 'vies']
    validation_schedule VARCHAR(20) NOT NULL, -- daily, weekly, monthly, custom
    custom_interval_hours INTEGER, -- For custom schedules
    last_validated_at TIMESTAMP,
    next_validation_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, company_id)
);

-- Premium callback queue
CREATE TABLE callback_queue (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    company_nip VARCHAR(10) NOT NULL,
    providers TEXT[] NOT NULL, -- ['regon', 'mf', 'vies']
    webhook_url TEXT NOT NULL,
    trigger_type VARCHAR(20) NOT NULL, -- scheduled, opportunistic, on_demand
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT
);

-- Webhook delivery history
CREATE TABLE webhook_deliveries (
    id BIGSERIAL PRIMARY KEY,
    callback_id BIGINT REFERENCES callback_queue(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    http_status INTEGER,
    response_body TEXT,
    response_headers JSONB,
    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL
);

-- API usage tracking
CREATE TABLE api_usage (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    token_id BIGINT REFERENCES api_tokens(id) ON DELETE CASCADE,
    company_nip VARCHAR(10),
    endpoint VARCHAR(100) NOT NULL,
    providers_requested TEXT[], -- Which providers were requested
    providers_fresh TEXT[], -- Which providers returned fresh data
    providers_cached TEXT[], -- Which providers returned cached data
    providers_rate_limited TEXT[], -- Which providers hit rate limits
    response_status INTEGER NOT NULL,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data change history (for webhooks)
CREATE TABLE data_changes (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL, -- regon, mf, vies, iban
    change_type VARCHAR(20) NOT NULL, -- created, updated, deleted
    field_changes JSONB, -- Diff of what changed
    old_data JSONB,
    new_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_companies_nip ON companies(nip);
CREATE INDEX idx_regon_data_company_id ON regon_data(company_id);
CREATE INDEX idx_regon_data_expires_at ON regon_data(expires_at);
CREATE INDEX idx_mf_data_company_id ON mf_data(company_id);
CREATE INDEX idx_mf_data_expires_at ON mf_data(expires_at);
CREATE INDEX idx_vies_data_company_id ON vies_data(company_id);
CREATE INDEX idx_vies_data_expires_at ON vies_data(expires_at);
CREATE INDEX idx_company_bank_accounts_company_id ON company_bank_accounts(company_id);
CREATE INDEX idx_company_bank_accounts_account_number ON company_bank_accounts(account_number);
CREATE INDEX idx_iban_enrichment_account_id ON iban_enrichment(account_id);
CREATE INDEX idx_iban_enrichment_expires_at ON iban_enrichment(expires_at);
CREATE INDEX idx_user_company_subscriptions_user_id ON user_company_subscriptions(user_id);
CREATE INDEX idx_user_company_subscriptions_company_id ON user_company_subscriptions(company_id);
CREATE INDEX idx_user_company_subscriptions_next_validation ON user_company_subscriptions(next_validation_at) WHERE is_active = TRUE;
CREATE INDEX idx_callback_queue_status ON callback_queue(status);
CREATE INDEX idx_callback_queue_next_retry_at ON callback_queue(next_retry_at);
CREATE INDEX idx_api_usage_user_id_created_at ON api_usage(user_id, created_at);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_data_changes_company_id ON data_changes(company_id);
CREATE INDEX idx_data_changes_provider ON data_changes(provider);

-- JSONB indexes for better query performance
CREATE INDEX idx_regon_data_jsonb ON regon_data USING GIN(data);
CREATE INDEX idx_mf_data_jsonb ON mf_data USING GIN(data);
CREATE INDEX idx_vies_data_jsonb ON vies_data USING GIN(data);
CREATE INDEX idx_iban_enrichment_jsonb ON iban_enrichment USING GIN(enrichment_data);