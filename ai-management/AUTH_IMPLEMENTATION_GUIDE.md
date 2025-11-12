# Authentication Implementation Guide

**Quick Start Guide for Engineers**
**Reference:** See `AUTHENTICATION_ARCHITECTURE_SPEC.md` for full details

---

## Implementation Order

### 1. Login Page (2-3 hours)

**File:** `/frontend/src/pages/login.tsx`

```typescript
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/shared/Button';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoggingIn } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await login({ username: email, password });

      // Redirect to original page or dashboard
      const redirect = router.query.redirect as string;
      router.push(redirect || '/dashboard-new');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-2xl shadow-lg">
        <div>
          <h2 className="text-3xl font-bold text-center text-gray-900">
            Sign in to your account
          </h2>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
            </div>
          </div>

          <div>
            <Button
              type="submit"
              className="w-full"
              disabled={isLoggingIn}
            >
              {isLoggingIn ? 'Signing in...' : 'Sign in'}
            </Button>
          </div>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <a href="/signup" className="font-medium text-red-600 hover:text-red-500">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

### 2. Signup Page (3-4 hours)

**File:** `/frontend/src/pages/signup.tsx`

```typescript
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/shared/Button';
import toast from 'react-hot-toast';

export default function SignupPage() {
  const router = useRouter();
  const { register, isRegistering } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    institution: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        name: formData.name,
        institution: formData.institution,
      });

      toast.success('Account created successfully!');
      router.push('/onboarding/researcher');
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Signup failed';
      toast.error(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-2xl shadow-lg">
        <div>
          <h2 className="text-3xl font-bold text-center text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join the Meta-Analysis Research Platform
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Full name *
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label htmlFor="institution" className="block text-sm font-medium text-gray-700">
                Institution
              </label>
              <input
                id="institution"
                name="institution"
                type="text"
                value={formData.institution}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
              </p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm password *
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
              />
            </div>
          </div>

          <div>
            <Button
              type="submit"
              className="w-full"
              disabled={isRegistering}
            >
              {isRegistering ? 'Creating account...' : 'Create account'}
            </Button>
          </div>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="font-medium text-red-600 hover:text-red-500">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

### 3. Protected Route Middleware (1-2 hours)

**File:** `/frontend/src/middleware/withAuth.tsx`

```typescript
import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import { canAccessAdmin, canAccessEditor } from '@/lib/rbac';
import { User } from '@/lib/types';

interface WithAuthOptions {
  requiredRole?: 'admin' | 'editor' | 'researcher';
  redirectTo?: string;
}

export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: WithAuthOptions
) {
  return function ProtectedRoute(props: P) {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !user) {
        // Redirect to login with original URL
        const redirectUrl = encodeURIComponent(router.asPath);
        router.push(`/login?redirect=${redirectUrl}`);
        return;
      }

      if (!isLoading && user && options?.requiredRole) {
        const hasPermission = checkPermission(user, options.requiredRole);
        if (!hasPermission) {
          router.push(options.redirectTo || '/dashboard-new');
        }
      }
    }, [user, isLoading, router]);

    // Show loading state
    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
        </div>
      );
    }

    // Don't render if no user
    if (!user) {
      return null;
    }

    // Check role permission
    if (options?.requiredRole) {
      const hasPermission = checkPermission(user, options.requiredRole);
      if (!hasPermission) {
        return null;
      }
    }

    return <Component {...props} />;
  };
}

function checkPermission(user: User, requiredRole: string): boolean {
  switch (requiredRole) {
    case 'admin':
      return canAccessAdmin(user);
    case 'editor':
      return canAccessEditor(user);
    case 'researcher':
      return true; // All authenticated users can access researcher pages
    default:
      return false;
  }
}
```

---

### 4. Update Existing Pages (1 hour)

**Protect Dashboard:**
```typescript
// frontend/src/pages/dashboard-new.tsx
import { withAuth } from '@/middleware/withAuth';

function DashboardPage() {
  // ... existing code
}

export default withAuth(DashboardPage);
```

**Protect Admin Dashboard:**
```typescript
// frontend/src/pages/admin/index.tsx
import { withAuth } from '@/middleware/withAuth';

function AdminDashboardPage() {
  // ... existing code
}

export default withAuth(AdminDashboardPage, { requiredRole: 'admin' });
```

**Protect Editor Dashboard:**
```typescript
// frontend/src/pages/editor/index.tsx
import { withAuth } from '@/middleware/withAuth';

function EditorPage() {
  // ... existing code
}

export default withAuth(EditorPage, { requiredRole: 'editor' });
```

---

### 5. Update Landing Page (30 minutes)

**File:** `/frontend/src/pages/landing.tsx`

```typescript
// Add buttons to hero section
<div className="flex gap-4">
  <Button
    onClick={() => router.push('/signup')}
    size="lg"
  >
    Get Started
  </Button>
  <Button
    onClick={() => router.push('/login')}
    variant="outline"
    size="lg"
  >
    Sign In
  </Button>
</div>
```

---

## Testing Checklist

### Manual Testing

**Registration Flow:**
1. [ ] Go to `/signup`
2. [ ] Fill in email, name, password (weak) → Should show error
3. [ ] Fill in email, name, password (strong) → Should succeed
4. [ ] Redirected to `/onboarding/researcher`
5. [ ] Complete onboarding → Redirected to `/dashboard-new`

**Login Flow:**
1. [ ] Go to `/login`
2. [ ] Enter wrong credentials → Should show error
3. [ ] Enter correct credentials → Should succeed
4. [ ] Redirected to `/dashboard-new`
5. [ ] Refresh page → Should stay logged in

**Protected Routes:**
1. [ ] Visit `/dashboard-new` without login → Redirected to `/login`
2. [ ] Visit `/admin` without login → Redirected to `/login`
3. [ ] Login as researcher → Visit `/admin` → Redirected to `/dashboard-new`
4. [ ] Login as admin → Visit `/admin` → Should show admin dashboard

**Logout Flow:**
1. [ ] Click logout button → Tokens cleared
2. [ ] Visit `/dashboard-new` → Redirected to `/login`

### Automated Testing

```typescript
// Example test with Vitest
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginPage from '@/pages/login';

describe('LoginPage', () => {
  it('should show error for wrong credentials', async () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <LoginPage />
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });
    fireEvent.click(screen.getByText(/sign in/i));

    await waitFor(() => {
      expect(screen.getByText(/login failed/i)).toBeInTheDocument();
    });
  });
});
```

---

## Environment Setup

### Backend

```bash
cd backend

# Create .env file
cp .env.example .env

# Generate secret key
openssl rand -hex 32

# Update .env
SECRET_KEY=<generated-key>
DATABASE_URL=postgresql://user:pass@localhost:5432/meta_analysis_db
REDIS_URL=redis://localhost:6379/0
```

### Frontend

```bash
cd frontend

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

---

## API Testing with cURL

### Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "institution": "MIT"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123"
```

### Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Access Admin Endpoint

```bash
curl -X GET http://localhost:8000/api/v1/admin/dashboard \
  -H "Authorization: Bearer <access_token>"
```

---

## Common Issues & Solutions

### Issue 1: CORS Error

**Symptom:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution:**
```bash
# Backend .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Issue 2: Token Expired

**Symptom:** 401 error after 30 minutes

**Solution:** Token refresh should happen automatically. Check axios interceptor in `lib/api.ts`

### Issue 3: Redirect Loop

**Symptom:** Page keeps redirecting to `/login`

**Solution:** Check if token is being stored in localStorage after login

### Issue 4: Admin Dashboard Shows 403

**Symptom:** Logged in but can't access `/admin`

**Solution:** Check user role in database. Default is RESEARCHER. Manually change to ADMIN:

```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'your@email.com';
```

---

## Database Queries for Testing

### Create Admin User

```sql
-- First, register via API, then:
UPDATE users
SET role = 'ADMIN', is_verified = true
WHERE email = 'admin@example.com';
```

### Create Test Users

```sql
-- Researcher (default)
INSERT INTO users (email, hashed_password, full_name, role)
VALUES ('researcher@example.com', '<hash>', 'Researcher User', 'RESEARCHER');

-- Editor
INSERT INTO users (email, hashed_password, full_name, role)
VALUES ('editor@example.com', '<hash>', 'Editor User', 'EDITOR');

-- Admin
INSERT INTO users (email, hashed_password, full_name, role)
VALUES ('admin@example.com', '<hash>', 'Admin User', 'ADMIN');
```

### View All Users

```sql
SELECT id, email, full_name, role, is_active, created_at
FROM users
ORDER BY created_at DESC;
```

---

## Performance Considerations

### Token Refresh Optimization

The current implementation refreshes on every 401. Consider pre-emptive refresh:

```typescript
// Add to lib/api.ts
let refreshTimeout: NodeJS.Timeout;

export function scheduleTokenRefresh(expiresIn: number) {
  clearTimeout(refreshTimeout);

  // Refresh 5 minutes before expiration
  const refreshIn = (expiresIn - 300) * 1000;

  refreshTimeout = setTimeout(async () => {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken
        });
        setAccessToken(response.data.access_token);
        scheduleTokenRefresh(response.data.expires_in);
      } catch (error) {
        // Refresh failed, logout
        clearTokens();
        window.location.href = '/login';
      }
    }
  }, refreshIn);
}
```

---

## Security Checklist

- [ ] All passwords hashed with Argon2
- [ ] JWT secret key is 32+ bytes
- [ ] HTTPS enforced in production
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] XSS protection (React escaping)
- [ ] SQL injection protection (Pydantic validation)
- [ ] Sensitive data not logged
- [ ] Token expiration enforced
- [ ] Admin endpoints require ADMIN role

---

## Deployment Checklist

### Backend (Railway)

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `DATABASE_URL` with production database
- [ ] Set `REDIS_URL` with production Redis
- [ ] Set `ALLOWED_ORIGINS` with frontend URL
- [ ] Set `DEBUG=false`
- [ ] Run migrations: `alembic upgrade head`
- [ ] Test health endpoint: `/api/v1/health`

### Frontend (Vercel)

- [ ] Set `NEXT_PUBLIC_API_URL` with backend URL
- [ ] Test build: `npm run build`
- [ ] Deploy to Vercel
- [ ] Test authentication flow in production

---

## Support & Documentation

**Full Specification:** `/ai-management/AUTHENTICATION_ARCHITECTURE_SPEC.md`

**Backend Code:**
- Auth endpoints: `/backend/app/api/v1/auth.py`
- Security utils: `/backend/app/core/security.py`
- User model: `/backend/app/models/user.py`

**Frontend Code:**
- useAuth hook: `/frontend/src/hooks/useAuth.ts`
- API client: `/frontend/src/lib/api.ts`
- RBAC utils: `/frontend/src/lib/rbac.ts`

**Questions?** Contact CTO or refer to architecture spec.

---

**Good luck with implementation!** 🚀
