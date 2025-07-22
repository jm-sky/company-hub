# Google reCAPTCHA Implementation Plan

## Overview

This document outlines the implementation plan for Google reCAPTCHA integration in CompanyHub to protect forms and API endpoints from bot abuse and spam. The implementation covers both FastAPI backend validation and Next.js frontend integration.

## Architecture

```
reCAPTCHA Flow:
1. Frontend renders reCAPTCHA widget on forms → User completes challenge
2. Frontend receives reCAPTCHA token → Includes token in form submission
3. Backend validates token with Google API → Checks score/success
4. Backend processes request or rejects with error → Returns response to frontend
```

## reCAPTCHA Versions

### reCAPTCHA v3 (Recommended)
- **Invisible**: No user interaction required
- **Score-based**: Returns score 0.0-1.0 (1.0 = human, 0.0 = bot)
- **User Experience**: Seamless, no challenges
- **Use Cases**: All form submissions, API endpoints

### reCAPTCHA v2 (Fallback)
- **Checkbox**: "I'm not a robot" checkbox
- **Challenge**: Image/audio challenges when needed
- **Score-based**: Returns true/false
- **Use Cases**: High-risk actions, when v3 score is low

## Backend (FastAPI) Implementation

### 1. Dependencies & Configuration

**Required packages:**
```bash
pip install httpx pydantic-settings
```

**Environment variables:**
```env
# Google reCAPTCHA Configuration
RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key
RECAPTCHA_VERIFY_URL=https://www.google.com/recaptcha/api/siteverify
RECAPTCHA_ENABLED=true
RECAPTCHA_MIN_SCORE=0.5
RECAPTCHA_TIMEOUT=10
```

### 2. Core Backend Components

**File: `app/security/recaptcha.py`**
- reCAPTCHA token verification service
- Score validation and threshold checking
- Response caching and rate limiting
- Error handling and logging

**File: `app/middleware/recaptcha.py`**
- FastAPI dependency for reCAPTCHA validation
- Configurable score thresholds per endpoint
- Bypass logic for development/testing

**File: `app/models/recaptcha.py`**
- Pydantic models for reCAPTCHA requests/responses
- Validation schemas for different use cases

### 3. reCAPTCHA Service Implementation

```python
# app/security/recaptcha.py
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class ReCaptchaService:
    def __init__(self):
        self.secret_key = settings.RECAPTCHA_SECRET_KEY
        self.verify_url = settings.RECAPTCHA_VERIFY_URL
        self.min_score = settings.RECAPTCHA_MIN_SCORE
        self.timeout = settings.RECAPTCHA_TIMEOUT
    
    async def verify_token(
        self, 
        token: str, 
        remote_ip: Optional[str] = None,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify reCAPTCHA token with Google API"""
        
    async def validate_score(
        self, 
        token: str, 
        min_score: float = None,
        action: str = None
    ) -> bool:
        """Validate reCAPTCHA score meets threshold"""
```

### 4. FastAPI Dependencies

```python
# app/middleware/recaptcha.py
from fastapi import Depends, HTTPException, Request
from app.security.recaptcha import ReCaptchaService

async def verify_recaptcha(
    request: Request,
    recaptcha_token: str = Form(...),
    min_score: float = 0.5,
    action: str = "submit"
):
    """FastAPI dependency for reCAPTCHA verification"""
    
    if not settings.RECAPTCHA_ENABLED:
        return True
    
    recaptcha_service = ReCaptchaService()
    is_valid = await recaptcha_service.validate_score(
        token=recaptcha_token,
        min_score=min_score,
        action=action
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="reCAPTCHA validation failed"
        )
    
    return True
```

### 5. Protected Endpoints

```python
# Example: Protecting company search endpoint
@router.post("/companies/search")
async def search_companies(
    query: CompanySearchRequest,
    recaptcha_valid: bool = Depends(verify_recaptcha),
    current_user: User = Depends(get_current_user)
):
    """Search companies with reCAPTCHA protection"""
    return await company_service.search(query)

# Example: Protecting registration endpoint
@router.post("/auth/register")
async def register_user(
    user_data: UserCreateRequest,
    recaptcha_valid: bool = Depends(
        partial(verify_recaptcha, min_score=0.7, action="register")
    )
):
    """Register new user with high reCAPTCHA threshold"""
    return await auth_service.register(user_data)
```

### 6. Configuration by Endpoint

**High Security (min_score: 0.8-0.9):**
- User registration
- Password reset requests
- Contact form submissions
- API key generation

**Medium Security (min_score: 0.5-0.7):**
- Company data requests
- User profile updates
- Search queries
- General form submissions

**Low Security (min_score: 0.3-0.4):**
- Public data access
- Read-only operations
- Cached responses

## Frontend (Next.js) Implementation

### 1. Dependencies & Configuration

**Required packages:**
```bash
pnpm add react-google-recaptcha-v3
```

**Environment variables:**
```env
# Google reCAPTCHA Configuration
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=your_recaptcha_site_key
NEXT_PUBLIC_RECAPTCHA_ENABLED=true
```

### 2. Core Frontend Components

**File: `lib/recaptcha.ts`**
- reCAPTCHA initialization and management
- Token generation utilities
- Score handling and fallbacks

**File: `components/recaptcha/ReCaptchaProvider.tsx`**
- React context for reCAPTCHA functionality
- Global reCAPTCHA state management

**File: `hooks/useRecaptcha.ts`**
- Custom hook for reCAPTCHA token generation
- Action-specific token requests
- Error handling and retries

### 3. reCAPTCHA Provider Setup

```typescript
// components/recaptcha/ReCaptchaProvider.tsx
import { GoogleReCaptchaProvider } from 'react-google-recaptcha-v3';

export default function ReCaptchaProvider({ children }: { children: React.ReactNode }) {
  if (!process.env.NEXT_PUBLIC_RECAPTCHA_ENABLED) {
    return <>{children}</>;
  }

  return (
    <GoogleReCaptchaProvider
      reCaptchaKey={process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!}
      scriptProps={{
        async: false,
        defer: false,
        appendTo: "head",
        nonce: undefined,
      }}
    >
      {children}
    </GoogleReCaptchaProvider>
  );
}
```

### 4. Custom Hook Implementation

```typescript
// hooks/useRecaptcha.ts
import { useGoogleReCaptcha } from 'react-google-recaptcha-v3';
import { useCallback } from 'react';

export const useRecaptcha = () => {
  const { executeRecaptcha } = useGoogleReCaptcha();

  const getToken = useCallback(async (action: string = 'submit'): Promise<string | null> => {
    if (!executeRecaptcha || !process.env.NEXT_PUBLIC_RECAPTCHA_ENABLED) {
      return null;
    }

    try {
      const token = await executeRecaptcha(action);
      return token;
    } catch (error) {
      console.error('reCAPTCHA execution failed:', error);
      return null;
    }
  }, [executeRecaptcha]);

  const isEnabled = Boolean(process.env.NEXT_PUBLIC_RECAPTCHA_ENABLED);

  return { getToken, isEnabled };
};
```

### 5. Form Integration Examples

**Registration Form:**
```typescript
// components/auth/RegisterForm.tsx
import { useRecaptcha } from '@/hooks/useRecaptcha';

export default function RegisterForm() {
  const { getToken } = useRecaptcha();
  const { mutate: register, isPending } = useRegister();

  const handleSubmit = async (data: RegisterFormData) => {
    const recaptchaToken = await getToken('register');
    
    register({
      ...data,
      recaptcha_token: recaptchaToken,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <Button type="submit" disabled={isPending}>
        Register
      </Button>
    </form>
  );
}
```

**Company Search Form:**
```typescript
// components/company/CompanySearchForm.tsx
import { useRecaptcha } from '@/hooks/useRecaptcha';

export default function CompanySearchForm() {
  const { getToken } = useRecaptcha();
  const { mutate: searchCompanies } = useCompanySearch();

  const handleSearch = async (query: string) => {
    const recaptchaToken = await getToken('search');
    
    searchCompanies({
      query,
      recaptcha_token: recaptchaToken,
    });
  };

  return (
    <SearchInput 
      onSearch={handleSearch}
      placeholder="Enter NIP or company name"
    />
  );
}
```

### 6. API Client Integration

```typescript
// lib/api.ts - Update API client to include reCAPTCHA tokens
export class ApiClient {
  async searchCompanies(params: {
    query: string;
    recaptcha_token?: string | null;
  }): Promise<ApiResponse<CompanySearchResponse>> {
    const formData = new FormData();
    formData.append('query', params.query);
    
    if (params.recaptcha_token) {
      formData.append('recaptcha_token', params.recaptcha_token);
    }

    const response = await this.client.post('/api/v1/companies/search', formData);
    return response.data;
  }
}
```

## Security Considerations

### Backend Security
- **Token Validation**: Always validate tokens server-side
- **Score Thresholds**: Use appropriate scores per endpoint
- **Rate Limiting**: Combine with rate limiting for enhanced protection
- **Logging**: Log reCAPTCHA failures for monitoring
- **Secret Protection**: Never expose secret key to frontend

### Frontend Security
- **Site Key**: Only expose site key (public by design)
- **Token Handling**: Don't log or store tokens long-term
- **Fallback Handling**: Graceful degradation when reCAPTCHA fails
- **HTTPS Only**: reCAPTCHA requires HTTPS in production

### Score Interpretation
```python
# Recommended score thresholds
SCORE_THRESHOLDS = {
    'high_security': 0.8,    # Registration, password reset
    'medium_security': 0.5,  # Search, data requests
    'low_security': 0.3,     # Public endpoints
    'suspicious': 0.1        # Likely bot traffic
}
```

## Error Handling

### Common Error Scenarios
1. **Network failures** - Google API unavailable
2. **Invalid tokens** - Expired or malformed tokens
3. **Low scores** - Potential bot traffic
4. **Rate limiting** - Too many requests to Google API
5. **Configuration errors** - Invalid keys or settings

### Error Response Format
```typescript
{
  "success": false,
  "message": "reCAPTCHA validation failed",
  "error_code": "RECAPTCHA_FAILED",
  "details": {
    "score": 0.2,
    "threshold": 0.5,
    "action": "register"
  }
}
```

### Fallback Strategies
1. **Development Mode**: Disable reCAPTCHA for local development
2. **Graceful Degradation**: Allow requests when reCAPTCHA service is down
3. **Manual Review**: Flag suspicious requests for manual review
4. **Alternative Protection**: Use rate limiting as backup

## Testing Strategy

### Backend Testing
- Unit tests for reCAPTCHA service
- Mock Google API responses
- Score threshold validation tests
- Integration tests with protected endpoints
- Performance tests under load

### Frontend Testing
- Mock reCAPTCHA provider in tests
- Form submission with/without tokens
- Error handling scenarios
- Accessibility testing
- Cross-browser compatibility

### End-to-End Testing
```typescript
// Example: E2E test with reCAPTCHA
test('user registration with reCAPTCHA', async ({ page }) => {
  // Mock reCAPTCHA for testing
  await page.addInitScript(() => {
    window.grecaptcha = {
      ready: (cb) => cb(),
      execute: () => Promise.resolve('test-token')
    };
  });

  await page.goto('/auth/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('[type="submit"]');
  
  await expect(page).toHaveURL('/dashboard');
});
```

## Monitoring & Analytics

### Metrics to Track
- **reCAPTCHA score distribution** - Monitor bot vs human traffic
- **Validation success rates** - Track API reliability
- **Score thresholds effectiveness** - Optimize based on false positives
- **Performance impact** - Monitor response times
- **User experience** - Track form completion rates

### Logging Strategy
```python
# Example: Structured logging for reCAPTCHA events
logger.info("recaptcha_validation", extra={
    "token_valid": True,
    "score": 0.8,
    "action": "register",
    "threshold": 0.7,
    "remote_ip": request.client.host,
    "user_agent": request.headers.get("user-agent"),
    "response_time_ms": 150
})
```

## Deployment Considerations

### Production Configuration
- **Domain Registration**: Register production domains with Google
- **HTTPS Requirements**: reCAPTCHA requires HTTPS
- **CDN Configuration**: Ensure reCAPTCHA scripts load properly
- **Environment Variables**: Secure key management
- **Monitoring Setup**: Alert on high failure rates

### Performance Optimization
- **Script Loading**: Optimize reCAPTCHA script loading
- **Caching**: Cache verification results temporarily
- **Async Operations**: Non-blocking token verification
- **Retry Logic**: Handle temporary API failures

## Cost Considerations

### Google reCAPTCHA Pricing
- **Free Tier**: 1M API calls per month
- **Paid Tier**: $1 per 1,000 additional calls
- **Enterprise**: Advanced features and support

### Optimization Strategies
- **Selective Protection**: Only protect high-risk endpoints
- **Score-based Actions**: Use appropriate thresholds
- **Caching**: Cache verification results when possible
- **Monitoring**: Track usage to optimize costs

## Migration Strategy

1. **Phase 1**: Implement backend reCAPTCHA service
2. **Phase 2**: Add frontend reCAPTCHA provider and hooks
3. **Phase 3**: Protect registration and high-risk endpoints
4. **Phase 4**: Extend to search and data endpoints
5. **Phase 5**: Monitor and optimize based on usage patterns

## Future Enhancements

- **Enterprise reCAPTCHA**: Advanced fraud detection
- **Custom Challenges**: Branded challenge experiences
- **Machine Learning**: Score-based automated actions
- **A/B Testing**: Optimize threshold values
- **Analytics Integration**: Enhanced bot detection insights
- **Mobile SDK**: Native mobile app protection