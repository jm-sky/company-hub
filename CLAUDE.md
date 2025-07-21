# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CompanyHub is a centralized API service for fetching, aggregating, and providing company data from public sources in Poland. It's a FastAPI-based Python application that supports REST API, webhooks, caching, and a user panel.

## Architecture

This is a documentation-first project currently in the planning phase. The system is designed around:

- **Tech Stack**: Python + FastAPI (Backend), Next.js + TypeScript (Frontend)
- **UI**: Next.js with shadcn/ui components and Tailwind CSS v4
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

## Package Management

- **Frontend**: Use `pnpm` for package management (not npm or yarn)
- **Backend**: Use `pip` with requirements.txt files

## Frontend Development Guidelines

### Styling Standards
- **Use Tailwind v4 size utilities**: `size-4` instead of `h-4 w-4`
- **Use semantic design system colors**: 
  - `text-destructive` instead of `text-red-500`
  - `text-muted-foreground` for secondary text
  - `text-brand` for brand colors
  - `border-destructive` for error borders
  - `bg-background` for main background
- **Use shadcn/ui semantic classes**: Follow the design system tokens
- **Consistent spacing**: Use spacing scale (space-y-4, gap-2, etc.)
- **Responsive design**: Mobile-first approach with sm:, md:, lg: breakpoints

### Component Architecture
- **shadcn/ui components**: Use for all UI elements (Button, Input, Card, Alert, etc.)
- **TypeScript**: Strict typing for all components and API calls
- **React Hook Form + Zod**: For form validation and handling
- **React Query**: For server state management and caching
- **Proper error handling**: Use Alert components for user feedback

### Internationalization Plan
- **Phase 1**: Build in English only (current)
- **Phase 2**: Add Polish (primary) + English before MVP launch
- **Phase 3**: Add Russian if user demand justifies it
- **Target**: Polish-first approach (90% of users from Poland)

### Additional Component Libraries

#### Origin UI (https://github.com/origin-space/originui)
- **Components**: Input (59), Button (54), general UI elements
- **No specific auth components** - use base components for forms
- **Usage**: Copy `.tsx` files to `components/ui`, add CSS variables
- **Compatible with**: shadcn/ui, Tailwind CSS v4

#### MVP Blocks (https://github.com/subhadeeproy3902/mvpblocks)
- **Components**: Claims 100+ blocks but no visible auth-specific components
- **Tech**: Next.js, TypeScript, TailwindCSS, Framer Motion
- **Usage**: Copy blocks directly into project
- **Status**: Repository structure unclear, no specific auth components identified

**Recommendation**: Current auth pages are well-implemented. Component libraries offer visual enhancements but no auth-specific functionality. Priority: complete real JWT authentication first.

## API & Type Patterns

### Frontend API Client (`/lib/api.ts`)
- **Standard Response Pattern**: All API endpoints return `ApiResponse<T>` where T is the specific data type
- **Consistency**: Always use the generic `ApiResponse<T>` wrapper, never create custom response types
- **Company Endpoint**: Returns `ApiResponse<CompanyResponse>` where CompanyResponse contains `data` and `metadata`

### Type Definitions (`/types/api.ts`)
- **Single Source of Truth**: All API types must be defined here
- **Backend Matching**: Frontend types should match backend response structures
- **Standard Wrapper**: `ApiResponse<T>` wraps all API responses with `data`, `message?`, and `success` fields

### Example Usage:
```typescript
// API Client
async getCompany(nip: string): Promise<ApiResponse<CompanyResponse>> {
  const response = await this.client.get(`/api/v1/companies/${nip}`);
  return response.data;
}

// ALWAYS use existing hooks instead of direct API calls
import { useCompany, useCompanyRefresh } from '@/lib/hooks/useCompanies';

// Component Usage - CORRECT
const { data: companyResponse, isLoading, error } = useCompany(nip);
// companyResponse is already CompanyResponse (data + metadata)

// Component Usage - WRONG (don't duplicate query logic)
const { data } = useQuery({
  queryFn: () => apiClient.getCompany(nip)  // ❌ Hook already exists!
});
```

### Existing Hooks to Use:
- `useCompany(nip)` - Get company data
- `useCompanyRefresh()` - Refresh company data  
- `useCompanySearch(query)` - Search companies
- `useAuth()` - Authentication state
- `useUser()` - User profile data

## Common Patterns & Anti-Patterns

### ✅ DO:
- **Check existing hooks** in `/lib/hooks/` before creating new queries
- **Check existing components** in `/components/` before creating new ones
- **Use TypeScript types** from `/types/api.ts` consistently
- **Follow shadcn/ui patterns** for component structure
- **Use semantic design tokens** (`text-destructive`, `bg-muted`, etc.)
- **Use existing scripts** like `/app/db/seed.py` instead of duplicating logic
- **Add empty line at EOF** for all files

### ❌ DON'T:
- **Duplicate query logic** when hooks already exist
- **Create custom response types** when `ApiResponse<T>` exists
- **Use direct API calls** in components (use hooks instead)
- **Hardcode colors** (use design system tokens)
- **Create new files** unnecessarily (prefer editing existing ones)
- **Mix SQLAlchemy models with Pydantic schemas** in union types (causes Pydantic errors)
- **Auto-redirect on 401 for auth endpoints** (login/register expect 401 responses)

### Type Safety Patterns:
```typescript
// Safe access to unknown Record types
const getProperty = (data: Record<string, unknown>, key: string): string | null => {
  if (key in data && typeof data[key] === 'string') {
    return data[key] as string;
  }
  return null;
};

// Usage
const name = getProperty(companyResponse.data.regon, 'name');
```

## Deployment Strategy

Planned deployment approach:
- VPS hosting (Hetzner, OVH)
- Docker containerization
- GitHub Actions for CI/CD
- Monitoring for uptime, queues, and webhook delivery