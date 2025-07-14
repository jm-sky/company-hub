# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CompanyHub is a centralized API service for fetching, aggregating, and providing company data from public sources in Poland. It's a FastAPI-based Python application that supports REST API, webhooks, caching, and a user panel.

## Architecture

This is a documentation-first project currently in the planning phase. The system is designed around:

- **Tech Stack**: Python + FastAPI
- **UI**: SSR + HTMX for lightweight, fast user panel
- **External Data Sources**: REGON (GUS API), MF (Biała Lista), VIES, IBAN API
- **Data Strategy**: Local caching with TTL, historical change tracking with diffs
- **API Design**: REST with versioning (`/api/v1/companies/{nip}`), JSON responses
- **Authentication**: API tokens (type TBD)
- **Background Processing**: Redis Queue/Celery for async tasks and webhooks

## Data Providers

### Core Company Data Providers:
1. **REGON (GUS API)** - Polish business registry
2. **MF (Biała Lista)** - Polish VAT whitelist  
3. **VIES** - EU VAT validation system (SOAP/XML)

### Enrichment Services:
4. **IBAN API** - Bank account enrichment for accounts found in MF data

Each provider has detailed documentation in `docs/providers/[provider]/`.

**Note:** IBAN API is used as an enrichment service to add bank details (name, currency, validation) to bank accounts returned by MF API, rather than as a direct company data provider.

## Key Features

- **Data Fetching**: On-demand (`GET /companies/{nip}`) and async CRON/queue
- **Caching**: Local TTL (1 day default), force refresh with `?refresh=true`
- **Webhooks**: `dataChanged`, `dataChanged.by.[provider]`, `dataChanged.in.[section]`
- **Rate Limiting**: Planned (Redis + token bucket)
- **History Tracking**: Diffs, timestamps, and source attribution for all changes

## Development Notes

- This repository currently contains only documentation and planning materials
- No source code has been implemented yet
- Architecture decisions are documented in `docs/architecture.md`
- Provider schemas and specifications are in `docs/providers/`
- The project follows Polish business data requirements and regulations

## Deployment Strategy

Planned deployment approach:
- VPS hosting (Hetzner, OVH)
- Docker containerization
- GitHub Actions for CI/CD
- Monitoring for uptime, queues, and webhook delivery