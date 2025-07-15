# Frontend Structure Plan

## Core Pages Structure

### Authentication Flow
- `/login` - User login
- `/register` - User registration  
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset form
- `/change-password` - Change password (authenticated)

### Main Application
- `/dashboard` - Main dashboard with company search
- `/companies/[nip]` - Company details page
- `/search` - Advanced company search
- `/history` - Search history

### Account Management
- `/profile` - User profile settings
- `/subscription` - Current subscription details
- `/billing` - Billing history and invoices
- `/checkout` - Subscription upgrade/purchase

### Developer Features
- `/api-keys` - API token management
- `/webhooks` - Webhook configuration
- `/documentation` - API docs integration

## Folder Structure
```
src/
├── app/
│   ├── (auth)/          # Auth pages group
│   ├── (dashboard)/     # Protected dashboard pages
│   ├── companies/       # Company-related pages
│   └── api/            # API routes (if needed)
├── components/
│   ├── ui/             # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── company/        # Company-specific components
│   └── dashboard/      # Dashboard components
├── lib/
│   ├── api.ts          # API client
│   ├── auth.ts         # Auth utilities
│   └── utils.ts        # General utilities
└── types/              # TypeScript types
```

## Tech Stack
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **State Management**: React Query for server state
- **Authentication**: JWT tokens
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **UI Components**: Custom components built with Tailwind

## Development Approach
1. Start with authentication pages
2. Build main dashboard structure
3. Implement company search and details
4. Add subscription management
5. Create developer features (API keys, webhooks)