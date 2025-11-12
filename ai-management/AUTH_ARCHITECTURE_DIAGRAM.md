# Authentication Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                   META-ANALYSIS RESEARCH PLATFORM                           │
│                   Authentication & Authorization System                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Authentication Flow Diagram

```
┌──────────────┐
│   Browser    │
│  (Frontend)  │
└──────┬───────┘
       │
       │ 1. User fills login form
       │    (email + password)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: /pages/login.tsx                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ const { login } = useAuth()                            │ │
│  │ login({ username: email, password })                   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 2. POST /api/v1/auth/login
                       │    Content-Type: application/x-www-form-urlencoded
                       │    Body: username=email&password=pass
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: /backend/app/api/v1/auth.py                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Find user by email in database                      │ │
│  │ 2. Verify password with Argon2                         │ │
│  │ 3. Create access token (30 min expiry)                 │ │
│  │ 4. Create refresh token (7 day expiry)                 │ │
│  │ 5. Update user.last_login                              │ │
│  │ 6. Return tokens                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 3. Response 200 OK
                       │    {
                       │      "access_token": "eyJhbGc...",
                       │      "refresh_token": "eyJhbGc...",
                       │      "token_type": "bearer",
                       │      "expires_in": 1800
                       │    }
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: /frontend/src/lib/api.ts                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ localStorage.setItem('access_token', token)            │ │
│  │ localStorage.setItem('refresh_token', token)           │ │
│  │ queryClient.setQueryData('currentUser', user)          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 4. Redirect to /dashboard-new
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  User sees dashboard (authenticated)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Protected Route Flow

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ User visits /dashboard-new
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: withAuth() middleware                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Check localStorage for access_token                 │ │
│  │ 2. If no token → Redirect to /login                    │ │
│  │ 3. If token exists → Validate with backend             │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ GET /api/v1/auth/me
                       │ Authorization: Bearer <access_token>
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: JWT Validation                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Extract token from Authorization header            │ │
│  │ 2. Verify JWT signature (HS256)                        │ │
│  │ 3. Check token expiration                              │ │
│  │ 4. Check token type (access vs refresh)               │ │
│  │ 5. Query user from database                            │ │
│  │ 6. Return user data                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Response 200 OK
                       │ { id, email, role, ... }
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: Render protected page                            │
│  - User authenticated                                       │
│  - Page rendered                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Token Refresh Flow

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ User makes API request
       │ (after 30 minutes)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: API Request with expired token                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ GET /api/v1/some-endpoint
                       │ Authorization: Bearer <expired_token>
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: Token validation fails                            │
│  Response 401 Unauthorized                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 401 Unauthorized
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: Axios Interceptor                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Detect 401 response                                 │ │
│  │ 2. Get refresh_token from localStorage                 │ │
│  │ 3. Call /auth/refresh endpoint                         │ │
│  │ 4. Store new access_token                              │ │
│  │ 5. Retry original request                              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ POST /api/v1/auth/refresh
                       │ Body: { "refresh_token": "..." }
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: Token Refresh                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Validate refresh_token                              │ │
│  │ 2. Check token type (must be REFRESH)                  │ │
│  │ 3. Verify user still active                            │ │
│  │ 4. Create new access_token                             │ │
│  │ 5. Create new refresh_token                            │ │
│  │ 6. Return new tokens                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Response 200 OK
                       │ { access_token, refresh_token, ... }
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend: Retry original request                           │
│  - New token stored                                         │
│  - Original request succeeds                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Role-Based Access Control (RBAC)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ROLE HIERARCHY                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌───────────┐                            │
│                    │   ADMIN   │                            │
│                    │  (Level 5) │                           │
│                    └─────┬─────┘                            │
│                          │ All permissions                  │
│                          │                                  │
│                    ┌─────▼─────┐                            │
│                    │  EDITOR   │                            │
│                    │  (Level 4) │                           │
│                    └─────┬─────┘                            │
│                          │ Edit & approve                   │
│                          │                                  │
│                    ┌─────▼──────┐                           │
│                    │ RESEARCHER │                           │
│                    │  (Level 3)  │                          │
│                    └─────┬──────┘                           │
│                          │ Create & manage own projects     │
│                          │                                  │
│                    ┌─────▼─────┐                            │
│                    │  REVIEWER │                            │
│                    │  (Level 2) │                           │
│                    └─────┬─────┘                            │
│                          │ Review & comment                 │
│                          │                                  │
│                    ┌─────▼─────┐                            │
│                    │   VIEWER  │                            │
│                    │  (Level 1) │                           │
│                    └───────────┘                            │
│                          │ Read-only                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Permission Matrix

```
┌──────────────────────┬───────┬────────┬────────────┬──────────┬────────┐
│     Permission       │ ADMIN │ EDITOR │ RESEARCHER │ REVIEWER │ VIEWER │
├──────────────────────┼───────┼────────┼────────────┼──────────┼────────┤
│ View own projects    │   ✓   │   ✓    │     ✓      │    ✓     │   ✓    │
│ Create projects      │   ✓   │   ✓    │     ✓      │    ✗     │   ✗    │
│ Edit own projects    │   ✓   │   ✓    │     ✓      │    ✗     │   ✗    │
│ Delete own projects  │   ✓   │   ✓    │     ✓      │    ✗     │   ✗    │
│ View all projects    │   ✓   │   ✓    │     ✗      │    ✗     │   ✗    │
│ Edit any project     │   ✓   │   ✓    │     ✗      │    ✗     │   ✗    │
│ Delete any project   │   ✓   │   ✗    │     ✗      │    ✗     │   ✗    │
│ Approve reviews      │   ✓   │   ✓    │     ✗      │    ✗     │   ✗    │
│ View admin dashboard │   ✓   │   ✗    │     ✗      │    ✗     │   ✗    │
│ Manage users         │   ✓   │   ✗    │     ✗      │    ✗     │   ✗    │
│ Manage subscriptions │   ✓   │   ✗    │     ✗      │    ✗     │   ✗    │
│ Distribute payouts   │   ✓   │   ✗    │     ✗      │    ✗     │   ✗    │
└──────────────────────┴───────┴────────┴────────────┴──────────┴────────┘
```

---

## 5. Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Next.js Pages                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ /login.tsx  │  │ /signup.tsx │  │ /dashboard  │             │
│  └─────────────┘  └─────────────┘  └──────┬──────┘             │
│                                            │                    │
│                                     (wrapped with withAuth)     │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Middleware: withAuth()                                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ - Check localStorage for tokens                           │ │
│  │ - Validate with backend (/auth/me)                        │ │
│  │ - Check role permissions (RBAC)                           │ │
│  │ - Redirect to /login if unauthenticated                   │ │
│  │ - Redirect to /dashboard if unauthorized                  │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  React Query Hooks                                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ useAuth() - Login/Register/Logout mutations               │ │
│  │ useQuery('currentUser') - Cache user state                │ │
│  │ useAdminDashboard() - Fetch admin data                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  API Client: axios                                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Request Interceptor:                                      │ │
│  │   - Add Authorization: Bearer <token> header             │ │
│  │                                                           │ │
│  │ Response Interceptor:                                     │ │
│  │   - Detect 401 → Refresh token → Retry request           │ │
│  │   - Detect 429 → Show rate limit error                   │ │
│  │   - Detect 403 → Show permission denied                  │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  localStorage                                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ access_token: "eyJhbGc..."                                │ │
│  │ refresh_token: "eyJhbGc..."                               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Backend Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ HTTP Request │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Middleware Stack (outermost to innermost)              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. ErrorHandlingMiddleware - Catch all errors            │ │
│  │ 2. PerformanceMiddleware - Track request times           │ │
│  │ 3. RequestIDMiddleware - Add unique request ID           │ │
│  │ 4. RateLimitMiddleware - Rate limit by user/IP           │ │
│  │ 5. CORSMiddleware - Handle CORS                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  API Routes: /api/v1/...                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ /auth/register   - Register new user                     │ │
│  │ /auth/login      - Login (OAuth2)                        │ │
│  │ /auth/refresh    - Refresh access token                  │ │
│  │ /auth/me         - Get current user (protected)          │ │
│  │ /auth/logout     - Logout (protected)                    │ │
│  │ /admin/dashboard - Admin dashboard (admin only)          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Dependencies (Dependency Injection)                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ get_current_user_token() - Validate JWT                  │ │
│  │ RoleChecker([UserRole.ADMIN]) - Check permissions        │ │
│  │ get_async_db() - Database session                        │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Security Layer                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ JWT Token Validation:                                     │ │
│  │   - Verify signature (HS256)                             │ │
│  │   - Check expiration                                      │ │
│  │   - Check token type (access vs refresh)                 │ │
│  │                                                           │ │
│  │ Password Hashing:                                         │ │
│  │   - Argon2id (OWASP recommended)                         │ │
│  │   - No length limits                                      │ │
│  │   - Memory-hard (GPU resistant)                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Database Layer (PostgreSQL)                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ users table:                                              │ │
│  │   - id (UUID)                                             │ │
│  │   - email (unique, indexed)                               │ │
│  │   - hashed_password                                       │ │
│  │   - role (ADMIN, EDITOR, RESEARCHER, REVIEWER, VIEWER)   │ │
│  │   - is_active, is_verified                                │ │
│  │   - created_at, updated_at, last_login                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      COMPLETE DATA FLOW                             │
└─────────────────────────────────────────────────────────────────────┘

User Registration Flow:
───────────────────────

Browser → /signup → POST /api/v1/auth/register
                         ↓
                    Validate password strength
                         ↓
                    Hash password (Argon2)
                         ↓
                    Insert into users table
                         ↓
                    Return user data (201)
                         ↓
Browser ← Redirect to /onboarding/researcher


User Login Flow:
────────────────

Browser → /login → POST /api/v1/auth/login
                        ↓
                   Find user by email
                        ↓
                   Verify password
                        ↓
                   Create access token (30 min)
                        ↓
                   Create refresh token (7 days)
                        ↓
                   Update last_login
                        ↓
                   Return tokens (200)
                        ↓
Browser ← Store tokens in localStorage
       ↓
     Redirect to /dashboard-new


Protected Request Flow:
───────────────────────

Browser → /dashboard-new → withAuth() middleware
                               ↓
                          Check localStorage for token
                               ↓
                          GET /api/v1/auth/me
                          Authorization: Bearer <token>
                               ↓
                          Validate JWT
                               ↓
                          Query user from database
                               ↓
                          Return user data (200)
                               ↓
Browser ← Render protected page


Token Refresh Flow:
───────────────────

Browser → API request → 401 Unauthorized
                            ↓
                       Axios interceptor
                            ↓
                       POST /api/v1/auth/refresh
                       Body: { refresh_token }
                            ↓
                       Validate refresh token
                            ↓
                       Create new access token
                            ↓
                       Return new tokens (200)
                            ↓
Browser ← Store new token
       ↓
     Retry original request


Admin Dashboard Flow:
─────────────────────

Browser → /admin → withAuth({ requiredRole: 'admin' })
                       ↓
                  Check user role
                       ↓
                  If not admin → Redirect to /dashboard
                       ↓
                  If admin → GET /api/v1/admin/dashboard
                       ↓
                  Require ADMIN role (backend)
                       ↓
                  Query platform metrics
                       ↓
                  Return dashboard data (200)
                       ↓
Browser ← Render admin dashboard
```

---

## 8. Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                                │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│ Layer 1: Transport Security (HTTPS)                              │
│ - TLS 1.2+ encryption                                             │
│ - All traffic encrypted in transit                                │
└───────────────────────────────────────────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────────────────┐
│ Layer 2: CORS & Rate Limiting                                     │
│ - Allow only whitelisted origins                                  │
│ - Rate limit: 100 req/min (authenticated)                         │
│ - Rate limit: 20 req/min (unauthenticated)                        │
│ - Redis-based distributed rate limiting                           │
└───────────────────────────────────────────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────────────────┐
│ Layer 3: Authentication (JWT)                                     │
│ - JWT tokens with HS256 signature                                 │
│ - Short-lived access tokens (30 min)                              │
│ - Long-lived refresh tokens (7 days)                              │
│ - Token type validation (access vs refresh)                       │
└───────────────────────────────────────────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────────────────┐
│ Layer 4: Authorization (RBAC)                                     │
│ - Role-based access control                                       │
│ - 5 roles: ADMIN, EDITOR, RESEARCHER, REVIEWER, VIEWER           │
│ - Middleware checks role before endpoint access                   │
│ - Database lookup for user permissions                            │
└───────────────────────────────────────────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────────────────┐
│ Layer 5: Data Security                                            │
│ - Password hashing: Argon2id (memory-hard)                        │
│ - No password length limits                                       │
│ - SQL injection protection (Pydantic validation)                  │
│ - XSS protection (React escaping)                                 │
│ - Sensitive data not logged                                       │
└───────────────────────────────────────────────────────────────────┘
```

---

## 9. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION DEPLOYMENT                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Internet   │
└──────┬───────┘
       │
       │ HTTPS (443)
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Vercel (Frontend)                                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Next.js Application                                       │ │
│  │ - /login, /signup pages                                   │ │
│  │ - Protected routes with withAuth()                        │ │
│  │ - API client with token management                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Environment Variables:                                         │
│  - NEXT_PUBLIC_API_URL=https://api.example.com                 │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             │ API Requests
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Railway (Backend)                                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ FastAPI Application                                       │ │
│  │ - /api/v1/auth/* endpoints                                │ │
│  │ - JWT validation middleware                               │ │
│  │ - RBAC enforcement                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Environment Variables:                                         │
│  - SECRET_KEY=<32-byte-random-key>                             │
│  - DATABASE_URL=postgresql://...                               │
│  - REDIS_URL=redis://...                                       │
│  - ALLOWED_ORIGINS=https://app.example.com                     │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────┐
                    │                        │                    │
                    ▼                        ▼                    ▼
        ┌───────────────────┐   ┌───────────────────┐   ┌──────────────┐
        │   PostgreSQL      │   │      Redis        │   │   Stripe     │
        │   (Database)      │   │  (Rate Limiting)  │   │  (Payments)  │
        └───────────────────┘   └───────────────────┘   └──────────────┘
```

---

## 10. Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING                                 │
└─────────────────────────────────────────────────────────────────────┘

Authentication Errors:
──────────────────────

400 Bad Request
├─ Email already registered → Show "Email already in use"
├─ Weak password → Show password requirements
└─ Invalid email format → Show "Invalid email"

401 Unauthorized
├─ Invalid token → Trigger token refresh
├─ Expired token → Trigger token refresh
├─ Missing token → Redirect to /login
└─ Wrong credentials → Show "Invalid email or password"

403 Forbidden
├─ Insufficient permissions → Show "Access denied"
└─ Inactive account → Show "Account inactive. Contact support"

404 Not Found
└─ User not found → Show "User not found"

429 Too Many Requests
└─ Rate limit exceeded → Show "Too many requests. Retry in X seconds"

500 Internal Server Error
└─ Server error → Show "Unexpected error. Please try again"


Frontend Error Flow:
────────────────────

API Request Error
       ↓
Axios Interceptor
       ↓
Check status code
       ↓
┌──────┴──────┐
│             │
▼             ▼
401?       Other error?
│             │
│             ▼
│      toast.error(message)
│
▼
Refresh token?
├─ Success → Retry request
└─ Failure → Clear tokens → Redirect to /login
```

---

**END OF ARCHITECTURE DIAGRAM**
