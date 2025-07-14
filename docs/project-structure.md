# Project Structure

## Recommended FastAPI Project Layout

```
company-hub/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration settings
│   ├── dependencies.py         # Common dependencies (auth, etc.)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Main v1 router
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── companies.py    # Company lookup endpoints
│   │   │       ├── auth.py         # Authentication endpoints
│   │   │       └── webhooks.py     # Webhook management
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── rate_limit.py   # Rate limiting middleware
│   │       └── auth.py         # JWT authentication middleware
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT handling, password hashing
│   │   ├── rate_limiter.py     # Rate limiting logic
│   │   └── exceptions.py       # Custom exceptions
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # Database connection
│   │   ├── models.py           # SQLAlchemy models
│   │   └── migrations/         # Alembic migrations
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py            # Base provider class
│   │   ├── regon.py           # REGON API integration
│   │   ├── mf.py              # MF API integration
│   │   ├── vies.py            # VIES API integration
│   │   └── iban.py            # IBAN API integration
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── company_service.py  # Main business logic
│   │   ├── cache_service.py    # Cache management
│   │   ├── webhook_service.py  # Webhook processing
│   │   └── auth_service.py     # Authentication logic
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── company.py          # Company response schemas
│   │   ├── auth.py             # Authentication schemas
│   │   └── webhook.py          # Webhook schemas
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py       # NIP validation, etc.
│       └── helpers.py          # Common utilities
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_api/
│   ├── test_providers/
│   └── test_services/
│
├── docs/                      # Current documentation
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables example
├── docker-compose.yml        # Docker setup
├── Dockerfile               # Container definition
└── README.md               # Project README
```

## Key Components

### 1. API Layer (`app/api/`)
- Versioned endpoints (`/api/v1/`)
- Request/response handling
- Input validation
- Middleware integration

### 2. Core Logic (`app/core/`)
- Security utilities (JWT, rate limiting)
- Custom exceptions
- Cross-cutting concerns

### 3. Data Layer (`app/db/`)
- Database models
- Connection management
- Migration scripts

### 4. Provider Integration (`app/providers/`)
- External API clients
- Provider-specific logic
- Error handling and retries

### 5. Business Services (`app/services/`)
- Main application logic
- Data aggregation
- Cache management
- Webhook processing

### 6. Data Models (`app/schemas/`)
- Pydantic models for API
- Request/response validation
- Type safety

## Development Workflow

1. **Start with models**: Define SQLAlchemy models based on schema
2. **Create base provider**: Implement base provider class
3. **Implement REGON provider**: First external integration
4. **Build company service**: Core business logic
5. **Add API endpoints**: REST API implementation
6. **Implement caching**: Redis integration
7. **Add authentication**: JWT middleware
8. **Rate limiting**: Redis-based rate limiting
9. **Webhook system**: Premium callback features

## Dependencies

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.0
redis>=5.0.0
pydantic>=2.5.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.25.0
python-multipart>=0.0.6
```

This structure provides:
- Clear separation of concerns
- Scalable architecture
- Easy testing
- Professional FastAPI patterns