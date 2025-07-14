# CompanyHub API

> Centralized API service for fetching, aggregating, and providing Polish company data from public sources.

**CompanyHub** is a FastAPI-based service that aggregates company data from multiple Polish government and EU sources, providing a unified REST API with intelligent caching, rate limiting, and webhook notifications.

## 🚀 Features

- **Multi-source data aggregation**: REGON (GUS), MF (Biała Lista), VIES, and IBAN enrichment
- **Intelligent caching**: 1-day TTL with premium bypass options
- **Smart rate limiting**: Time-based limits respecting external API constraints
- **Webhook notifications**: Real-time callbacks for data changes
- **Partial responses**: Get available data even when some providers are rate-limited
- **Premium subscriptions**: Scheduled validation and priority access

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │     Redis       │
│                 │    │                 │    │                 │
│  • REST API     │◄──►│  • Companies    │    │  • Rate limits  │
│  • Webhooks     │    │  • Cache data   │    │  • Sessions     │
│  • Rate limits  │    │  • User mgmt    │    │  • Temp data    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  REGON (GUS)    │    │   MF (Biała     │    │     VIES        │
│                 │    │    Lista)       │    │                 │
│  • Company data │    │  • VAT status   │    │  • EU VAT       │
│  • 2-step auth  │    │  • Bank accounts│    │  • Validation   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/company-hub.git
   cd company-hub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Create database
   createdb companyhub
   
   # Run migrations
   alembic upgrade head
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/companyhub

# External APIs
REGON_API_KEY=your-regon-api-key
IBAN_API_KEY=your-iban-api-key

# Security
SECRET_KEY=your-secret-key
```

## 📖 API Usage

### Get Company Data

```bash
# Basic request
curl "http://localhost:8000/api/v1/companies/1234567890"

# Force refresh specific providers
curl "http://localhost:8000/api/v1/companies/1234567890?refresh=regon,mf"

# Allow partial responses (200 instead of 429 on rate limits)
curl "http://localhost:8000/api/v1/companies/1234567890?partial=allow"
```

### Response Format

```json
{
  "data": {
    "nip": "1234567890",
    "regon": {
      "found": true,
      "entity_type": "P",
      "report_type": "BIR11OsPrawna",
      "detailed_data": { ... }
    },
    "mf": { ... },
    "vies": { ... },
    "bank_accounts": [ ... ]
  },
  "metadata": {
    "regon": {
      "status": "fresh",
      "fetched_at": "2024-01-15T10:30:00Z"
    },
    "mf": {
      "status": "cached",
      "cached_at": "2024-01-15T08:00:00Z"
    },
    "vies": {
      "status": "rate_limited",
      "next_available_at": "2024-01-15T10:35:00Z"
    }
  }
}
```

## 🎯 Data Providers

### Core Company Data
- **REGON (GUS API)**: Polish business registry with two-step authentication
- **MF (Biała Lista)**: Polish VAT whitelist with bank account data
- **VIES**: EU VAT validation system

### Enrichment Services
- **IBAN API**: Bank account validation and enrichment for accounts from MF data

## 📊 Rate Limiting

CompanyHub respects external API limits and implements intelligent rate limiting:

### REGON API Limits
- **Peak hours** (8:00-16:59): 3 req/sec, 120 req/min, 6000 req/hour
- **Off-peak 1** (6:00-7:59, 17:00-21:59): 3 req/sec, 150 req/min, 8000 req/hour
- **Off-peak 2** (22:00-5:59): 4 req/sec, 200 req/min, 10000 req/hour

### API Rate Limits
- **Free tier**: 5 requests/hour
- **Premium tier**: 1000 requests/hour

## 🔄 Caching Strategy

- **Default TTL**: 1 day for all providers
- **Bank account enrichment**: 7 days (changes less frequently)
- **Cache bypass**: Premium users can force refresh with `?refresh=provider`
- **Intelligent validation**: Only validate companies that premium users monitor

## 📢 Webhook System

Premium users can subscribe to data change notifications:

```json
{
  "webhook_url": "https://your-app.com/webhook",
  "providers": ["regon", "mf", "vies"],
  "schedule": "daily",
  "trigger_types": ["scheduled", "opportunistic", "on_demand"]
}
```

## 🧪 Development

### Project Structure

```
app/
├── api/v1/              # API endpoints
├── core/                # Security, rate limiting
├── db/                  # Database models, migrations
├── providers/           # External API integrations
├── schemas/             # Pydantic models
├── services/            # Business logic
└── utils/               # Utilities, validators
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Formatting
black app/
isort app/

# Linting
flake8 app/
mypy app/
```

## 🚢 Deployment

### Docker

```bash
# Build and run
docker-compose up --build

# Production mode
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup

- **Development**: SQLite + Redis
- **Production**: PostgreSQL + Redis + SSL

## 📈 Monitoring

Key metrics to monitor:

- **API response times** by provider
- **Rate limit hit rates**
- **Cache hit ratios**
- **Webhook delivery success rates**
- **Database query performance**

## 🔒 Security

- **JWT authentication** for API access
- **Rate limiting** per API token
- **Input validation** for all endpoints
- **SQL injection protection** via SQLAlchemy ORM
- **HTTPS enforcement** in production

## 📚 Documentation

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Architecture**: `docs/architecture.md`
- **Design Decisions**: `docs/design-decisions.md`
- **Database Schema**: `docs/database-schema.sql`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/company-hub/issues)
- **Documentation**: [Wiki](https://github.com/your-org/company-hub/wiki)
- **Email**: jan.madeyski@gmail.com

---

**Built with ❤️ using FastAPI, PostgreSQL, and Redis**
