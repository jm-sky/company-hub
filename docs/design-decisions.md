# Design Decisions - CompanyHub

## Database Architecture

### Provider-Specific Tables
- `companies` - Main table (NIP, basic info, timestamps)
- `regon_data` - REGON specific data with foreign key to companies
- `mf_data` - MF (Biała Lista) specific data
- `vies_data` - VIES specific data  
- `iban_data` - IBAN API specific data

### Authentication
- **JWT tokens** for stateless authentication
- Token payload includes: user/client ID, permissions, rate limits
- No database lookups needed for validation

## Rate Limiting Strategy

### REGON API Limits (from GUS)
**Peak hours (8:00-16:59):**
- 6000/hour, 120/minute, 3/second

**Off-peak 1 (6:00-7:59, 17:00-21:59):**
- 8000/hour, 150/minute, 3/second

**Off-peak 2 (22:00-5:59):**
- 10000/hour, 200/minute, 4/second

### Our API Rate Limits
- **Free tier:** 5 requests/hour
- **Premium tier:** Higher limits (TBD)
- **Scope:** Per API token
- **Implementation:** Real-time enforcement (no queue)

## Data & Caching Strategy

### Caching Approach
- **Default:** Return cached data (1 day TTL)
- **Premium users:** Can bypass cache with granular refresh params
- **Parameters:** `?refresh=regon,mf,vies` for selective refresh
- **IBAN enrichment:** Separate enrichment process for bank accounts from MF data

### Response Strategy
- **Partial responses:** Return available data + rate limit info for unavailable sources
- **Error handling:** User can pass `throw` param to get error response instead of 200 with partial data
- **Metadata:** Always include data freshness and rate limit information

### Premium Features
- **Fresh data:** Can request non-cached data
- **Callbacks:** Pre-configured webhook URLs per user
- **Priority:** Callback when fresh data becomes available after rate limit

## REGON Implementation Details

### Entity Types & Reports
```
EntityType::LegalPerson             => RegonReportName::BIR11LegalPerson
EntityType::NaturalPerson           => RegonReportName::BIR11NaturalPersonCeidg  
EntityType::LocalLegalPersonUnit    => RegonReportName::BIR11LocalLegalPersonUnit
EntityType::LocalNaturalPersonUnit  => RegonReportName::BIR11LocalNaturalPersonUnit
```

### Entity Type Mapping
- `P` - Osoba prawna (Legal Person)
- `F` - Osoba fizyczna (Natural Person) 
- `LP` - Jednostka lokalna osoby prawnej (Local Legal Person Unit)
- `LF` - Jednostka lokalna osoby fizycznej (Local Natural Person Unit)

### Report Names
- `BIR11OsPrawna` - Legal persons
- `BIR11OsFizycznaDzialalnoscCeidg` - Natural persons (CEIDG)
- `BIR11OsFizycznaDzialalnoscPozostala` - Natural persons (other)
- `BIR11OsFizycznaRolnicza` - Natural persons (agricultural)
- `BIR11JednLokalnaOsPrawnej` - Local units (legal persons)
- `BIR11JednLokalnaOsFizycznej` - Local units (natural persons)

### Data Storage
- **Full detailed data** from REGON API
- **MVP scope:** Start with NIP lookup only
- **Future:** Add REGON number and company name search

## API Response Format

### Successful Response with Partial Data
```json
{
  "data": {
    "regon": null,
    "mf": { /* cached data */ },
    "vies": { /* cached data */ },
    "iban": { /* cached data */ }
  },
  "metadata": {
    "regon": {
      "status": "rate_limited",
      "next_available_at": "2024-01-15T14:30:00Z",
      "cached_at": null
    },
    "mf": {
      "status": "cached", 
      "cached_at": "2024-01-15T08:00:00Z"
    },
    "vies": {
      "status": "cached",
      "cached_at": "2024-01-15T08:00:00Z"
    }
  }
}
```

## Technical Decisions

### Entity Type Detection
- **Two-step REGON process:** First query to get entity type, then specific report query
- **NIP validation:** Basic format validation before any API calls

### Rate Limiting Storage
- **Redis:** For token-based rate limiting (fast, expires automatically)

## My Suggestions

### REGON Table Structure
**Option A - Single table with JSON:**
```sql
CREATE TABLE regon_data (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id),
    entity_type VARCHAR(2), -- P, F, LP, LF
    report_type VARCHAR(50), -- BIR11OsPrawna, etc.
    data JSONB, -- Full report data
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

**Option B - Separate tables per entity type:**
```sql
CREATE TABLE regon_legal_persons (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id),
    regon VARCHAR(20),
    nazwa TEXT,
    -- ... specific fields for legal persons
);
```

**Recommendation:** **Option A (JSON)** - More flexible, easier to maintain, good PostgreSQL JSONB performance.

### Premium Callback Queue
**Option A - Database table:**
```sql
CREATE TABLE callback_queue (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    company_nip VARCHAR(10),
    providers TEXT[], -- ['regon', 'mf']
    webhook_url TEXT,
    created_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);
```

**Option B - Message queue (Redis/RabbitMQ):**
- Better for high-volume scenarios
- Built-in retry mechanisms
- Separate from main database

**Recommendation:** **Database table** for MVP, migrate to message queue if volume grows.

## Final Design Decisions

### Cache TTL Strategy
- **Uniform 1-day TTL** for all providers
- Simple to implement and understand
- Consistent behavior across all data sources

### Error Response Handling
**Default behavior:** Return 429 (Too Many Requests) with available data in response body

**Response format for rate-limited scenario:**
```json
{
  "error": "rate_limited",
  "message": "Some providers hit rate limits", 
  "data": {
    "regon": null,
    "mf": { /* cached data */ },
    "vies": { /* cached data */ }
  },
  "metadata": {
    "regon": {
      "status": "rate_limited",
      "next_available_at": "2024-01-15T14:30:00Z"
    },
    "mf": {
      "status": "cached",
      "cached_at": "2024-01-15T08:00:00Z"
    }
  }
}
```

**Optional parameter:** `?partial=allow` to get 200 status with partial data instead of 429

This approach:
- Clearly indicates rate limiting with proper HTTP status
- Still provides available data for immediate use
- Gives users control when they want to handle partial responses as success

## IBAN Enrichment Strategy

### Bank Account Enrichment Process
- **MF API returns:** Company data including bank account numbers
- **IBAN API enriches:** Bank account details (bank name, currency, location, validation)
- **Storage:** Separate bank accounts table linked to companies
- **Caching:** Bank details cached longer (7 days) - change less frequently than company data

### Enrichment Workflow
```
1. MF API returns company data with bank accounts: ["12345678901234567890"]
2. For each bank account → call IBAN API to get bank details
3. Store enriched bank account data separately
4. When serving company data → include enriched bank account info
5. Cache bank details separately with longer TTL
```

### Benefits
- **Richer data:** Bank names, currencies, validation status
- **Efficient caching:** Bank details change less frequently
- **Flexible enrichment:** Can add more bank data sources later
- **Cost optimization:** Only enrich bank accounts that appear in MF responses

## Premium User Validation Strategy

### Validation Triggers
- **On-demand validation:** When premium users request fresh data
- **Scheduled validation:** Based on user-configured schedule
- **Opportunistic validation:** When other users query the same company
- **No bulk validation:** Only validate companies that premium users care about

### User Configuration
- **Schedule options:** daily, weekly, monthly, custom intervals
- **Premium tiers:** Daily validation as premium feature
- **Opt-in only:** Users must explicitly enable scheduled validation
- **Per-company settings:** Different schedules for different companies

### Validation Logic
```
When company X is requested:
1. Check if any premium user has scheduled validation for company X
2. If data is stale according to their schedule → validate & send callbacks
3. If fresh data fetched → trigger callbacks for all premium users watching company X
4. Cache benefits everyone, callbacks only go to premium subscribers
```

### Database Changes Needed
- Add user subscription preferences (which companies, schedules)
- Track which premium users want callbacks for which companies
- Store user-specific validation schedules

## Implementation Priority

1. **Phase 1:** REGON integration with NIP lookup
2. **Phase 2:** Add other providers (MF, VIES, IBAN)
3. **Phase 3:** Advanced features (webhooks, premium callbacks)
4. **Phase 4:** User panel and billing integration