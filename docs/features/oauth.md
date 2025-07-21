# OAuth Implementation Plan

## Overview

This document outlines the implementation plan for OAuth authentication in CompanyHub, covering both the FastAPI backend and Next.js frontend components. The architecture is designed to support multiple OAuth providers (GitHub, Google, etc.) with a unified implementation.

## Architecture

```
OAuth Flow (GitHub/Google):
1. User clicks "Sign in with [Provider]" → Frontend redirects to OAuth provider
2. Provider redirects back with auth code → Backend exchanges code for tokens
3. Backend fetches user info from provider API → Creates/updates local user
4. Backend returns JWT token → Frontend stores token for API authentication
```

## Backend (FastAPI) Implementation

### 1. Dependencies & Configuration

**Required packages:**
```bash
pip install python-jose[cryptography] python-multipart httpx
```

**Environment variables:**
```env
# OAuth Providers
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback/github

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Database Schema Extensions

**Users table additions:**
```sql
-- OAuth provider fields
ALTER TABLE users ADD COLUMN github_id INTEGER UNIQUE;
ALTER TABLE users ADD COLUMN github_username VARCHAR(255);
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN google_email VARCHAR(255);

-- Shared OAuth fields
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255);
ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50); -- 'github', 'google', etc.
ALTER TABLE users ADD COLUMN oauth_access_token TEXT; -- Encrypted storage
ALTER TABLE users ADD COLUMN oauth_refresh_token TEXT; -- Encrypted storage
```

### 3. Core Backend Components

**File: `app/auth/oauth.py`**
- Abstract OAuth provider base class
- GitHub OAuth client implementation
- Google OAuth client implementation
- Token exchange functions (provider-agnostic)
- User profile fetching from provider APIs

**File: `app/auth/jwt.py`**
- JWT token creation/validation
- User authentication middleware

**File: `app/api/v1/auth.py`**
- OAuth callback endpoints:
  - `POST /api/v1/auth/github/callback`
  - `POST /api/v1/auth/google/callback`
- Token refresh endpoint: `POST /api/v1/auth/refresh`
- User profile endpoint: `GET /api/v1/auth/me`

**File: `app/models/user.py`**
- User model with OAuth provider fields
- OAuth user creation/update logic (multi-provider support)

### 4. API Endpoints

```python
# GitHub OAuth Callback
POST /api/v1/auth/github/callback
{
  "code": "github_auth_code",
  "state": "csrf_token"
}

# Google OAuth Callback  
POST /api/v1/auth/google/callback
{
  "code": "google_auth_code",
  "state": "csrf_token"
}

# Both endpoints return the same response format:
Response: {
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "oauth_provider": "github", // or "google"
    "github_username": "username", // if GitHub
    "google_email": "user@gmail.com", // if Google
    "avatar_url": "https://..."
  }
}

GET /api/v1/auth/me
Headers: Authorization: Bearer jwt_token
Response: {
  "id": 1,
  "email": "user@example.com",
  "oauth_provider": "github", // or "google"
  "github_username": "username", // if GitHub
  "google_email": "user@gmail.com", // if Google
  "avatar_url": "https://..."
}
```

### 5. Security Features

- CSRF protection with state parameter
- JWT token expiration and refresh
- Secure token storage (httpOnly cookies option)
- Rate limiting on auth endpoints
- Input validation with Pydantic models

## Frontend (Next.js) Implementation

### 1. Dependencies & Configuration

**Required packages:**
```bash
pnpm add @tanstack/react-query axios js-cookie
pnpm add -D @types/js-cookie
```

**Environment variables:**
```env
# OAuth Provider Configuration
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

### 2. Core Frontend Components

**File: `lib/auth.ts`**
- Multi-provider OAuth URL generation (GitHub, Google)
- Token management utilities
- Auth state management (provider-agnostic)

**File: `lib/hooks/useAuth.ts`**
- Authentication React Query hooks
- User profile management
- Token refresh logic

**File: `components/auth/OAuthButtons.tsx`**
- GitHub OAuth initiation button
- Google OAuth initiation button
- Unified styling and loading states

**File: `app/auth/callback/[provider]/page.tsx`**
- Dynamic OAuth callback handler (supports github, google)
- Code exchange and user redirect
- Provider-specific error handling

### 3. Authentication Flow

**Login Flow:**
```typescript
// 1. Generate OAuth URL with state (provider-agnostic)
const oauthUrl = generateOAuthUrl(provider); // 'github' or 'google'
// GitHub: https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=user:email&state=${csrfToken}
// Google: https://accounts.google.com/o/oauth2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&scope=email profile&state=${csrfToken}&response_type=code

// 2. Redirect user to OAuth provider
window.location.href = oauthUrl;

// 3. Handle callback (app/auth/callback/[provider]/page.tsx)
const { provider } = useParams(); // 'github' or 'google'
const { code, state } = useSearchParams();
const { mutate: exchangeCode } = useOAuthCallback(provider);
exchangeCode({ code, state });

// 4. Store JWT token and redirect
localStorage.setItem('access_token', response.access_token);
router.push('/dashboard');
```

**Protected Routes:**
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect('/auth/login');
  }
}
```

### 4. UI Components

**Login Page Features:**
- GitHub login button with brand styling
- Google login button with brand styling  
- Loading states during OAuth flow
- Error handling and user feedback
- "Continue with GitHub" and "Continue with Google" CTAs
- Provider selection UI

**User Profile Components:**
- Avatar display from OAuth provider
- Username/email display (provider-specific fields)
- OAuth provider indicator (GitHub/Google badge)
- Logout functionality
- Profile settings integration

### 5. State Management

**React Query Setup:**
```typescript
// hooks/useAuth.ts
export const useAuth = () => {
  return useQuery({
    queryKey: ['auth', 'user'],
    queryFn: fetchCurrentUser,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export const useOAuthCallback = (provider: 'github' | 'google') => {
  return useMutation({
    mutationFn: (data) => exchangeOAuthCode(provider, data),
    onSuccess: (data) => {
      queryClient.setQueryData(['auth', 'user'], data.user);
      // Handle token storage and redirect
    },
  });
};
```

## Security Considerations

### Backend Security
- Validate all OAuth provider webhooks and callbacks
- Implement rate limiting on auth endpoints
- Use secure JWT signing algorithms
- Store sensitive tokens encrypted (OAuth access/refresh tokens)
- Implement proper CORS configuration
- Provider-specific token validation

### Frontend Security
- Validate state parameter to prevent CSRF (all providers)
- Use secure token storage (httpOnly cookies preferred)
- Implement proper logout (token invalidation)
- Handle token expiration gracefully
- Sanitize user data from OAuth provider APIs
- Provider-specific security considerations (Google: verify JWT tokens)

## Error Handling

### Common Error Scenarios
1. **OAuth provider denial** - User cancels authorization (GitHub/Google)
2. **Invalid auth code** - Expired or tampered callback
3. **Provider API errors** - Service unavailable, rate limits (GitHub/Google APIs)
4. **JWT token expiration** - Automatic refresh or re-login
5. **Network failures** - Retry mechanisms and fallbacks
6. **Provider-specific errors** - Account verification, permissions

### Error Response Format
```typescript
{
  "success": false,
  "message": "Authentication failed",
  "error_code": "OAUTH_EXCHANGE_FAILED",
  "details": {
    "provider": "github", // or "google"
    "reason": "invalid_code"
  }
}
```

## Testing Strategy

### Backend Tests
- Unit tests for OAuth token exchange (GitHub, Google)
- Integration tests for provider API calls
- Authentication middleware tests
- JWT token validation tests
- Provider-specific flow tests

### Frontend Tests
- OAuth flow integration tests (multi-provider)
- Protected route access tests
- Token refresh functionality tests
- Error handling and fallback tests
- Provider selection and callback handling tests

## Deployment Considerations

### Production Configuration
- OAuth App registration for both providers (production URLs)
- Environment-specific redirect URIs for GitHub and Google
- SSL/TLS requirements for OAuth callbacks
- CDN and caching considerations for auth assets
- Provider-specific domain verification (Google)

### Monitoring & Logging
- OAuth success/failure rates per provider
- Token refresh frequency
- Provider API rate limit monitoring (GitHub, Google)
- Authentication error tracking by provider
- User registration patterns by OAuth provider

## Migration Strategy

1. **Phase 1**: Implement backend OAuth endpoints (GitHub first)
2. **Phase 2**: Add frontend GitHub login option
3. **Phase 3**: Add Google OAuth support (backend + frontend)
4. **Phase 4**: Migrate existing users to OAuth (optional)
5. **Phase 5**: Deprecate legacy authentication (if applicable)

## Provider-Specific Implementation Notes

### GitHub OAuth
- Scopes: `user:email` (basic profile + email access)
- API endpoint: `https://api.github.com/user`
- Token exchange: `https://github.com/login/oauth/access_token`

### Google OAuth
- Scopes: `email profile` (basic profile + email access)
- API endpoint: `https://www.googleapis.com/oauth2/v2/userinfo`
- Token exchange: `https://oauth2.googleapis.com/token`
- Additional: JWT token verification for enhanced security

## Future Enhancements

- Additional OAuth providers (Microsoft, LinkedIn)
- Social profile synchronization across providers
- GitHub repository access for advanced features
- Google Workspace integration
- Organization-based access control
- SSO integration for enterprise users