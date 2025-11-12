# Meta-Analysis Platform API Documentation

## Authentication & Admin API Endpoints

### Base URL
```
Production: https://your-domain.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Authentication Endpoints

### 1. Register New User
**POST** `/auth/register`

Register a new researcher account.

**Request Body:**
```json
{
  "email": "researcher@university.edu",
  "password": "SecurePass123!",
  "full_name": "Dr. Jane Smith",
  "institution": "Stanford University"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "researcher@university.edu",
  "full_name": "Dr. Jane Smith",
  "institution": "Stanford University",
  "role": "RESEARCHER",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-12T10:30:00Z",
  "last_login": null
}
```

**Error Responses:**
- `400 Bad Request` - Email already registered or invalid password
- `422 Unprocessable Entity` - Validation error

---

### 2. Login
**POST** `/auth/login`

Login with email and password (OAuth2 password flow).

**Request Body:** (form-data)
```
username: researcher@university.edu
password: SecurePass123!
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `401 Unauthorized` - Incorrect credentials
- `403 Forbidden` - Account inactive

---

### 3. Admin Login
**POST** `/auth/admin-login`

Dedicated login endpoint for administrators with elevated validation.

**Request Body:** (form-data)
```
username: admin@academic-platform.com
password: Admin123!
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `401 Unauthorized` - Incorrect credentials
- `403 Forbidden` - Not an admin account or account inactive

---

### 4. Refresh Token
**POST** `/auth/refresh`

Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired refresh token

---

### 5. Get Current User
**GET** `/auth/me`

Get authenticated user's profile information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "researcher@university.edu",
  "full_name": "Dr. Jane Smith",
  "institution": "Stanford University",
  "role": "RESEARCHER",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-11-12T10:30:00Z",
  "last_login": "2025-11-12T14:22:00Z"
}
```

---

### 6. Logout
**POST** `/auth/logout`

Logout current session (client should delete stored tokens).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** `204 No Content`

---

## Master Admin Endpoints

All admin endpoints require authentication with ADMIN role.

### 1. List Researchers
**GET** `/admin/researchers`

Get paginated list of all researchers with filtering.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Query Parameters:**
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 50, max: 100) - Results per page
- `search` (string) - Search by name, email, or institution
- `min_h_index` (int) - Filter by minimum h-index
- `country` (string) - Filter by country
- `connect_status` (string) - Filter by Stripe Connect status
- `sort_by` (string, default: "created_at") - Sort field
- `sort_order` (string, default: "desc") - Sort order (asc/desc)

**Example Request:**
```
GET /admin/researchers?search=stanford&min_h_index=20&limit=10
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Dr. Alan Turing",
    "email": "turing@stanford.edu",
    "institution": "Stanford University",
    "h_index": 42,
    "total_citations": 5420,
    "publication_count": 127,
    "total_review_count": 18,
    "total_earnings_cents": 125000,
    "connect_account_status": "active",
    "last_active": "2025-11-10",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

---

### 2. Get Researcher Details
**GET** `/admin/researchers/{researcher_id}`

Get detailed information about a specific researcher.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "orcid": "0000-0001-1111-1111",
  "name": "Dr. Alan Turing",
  "email": "turing@stanford.edu",
  "institution": "Stanford University",
  "department": "Computer Science",
  "country": "USA",
  "h_index": 42,
  "i10_index": 85,
  "total_citations": 5420,
  "publication_count": 127,
  "expertise_keywords": ["artificial intelligence", "machine learning"],
  "research_domains": ["AI", "Computer Science"],
  "total_review_count": 18,
  "recent_review_count": 3,
  "average_review_time_days": 21.5,
  "response_rate": 0.85,
  "stripe_connect_account_id": "acct_xxxxxxxxxxxxx",
  "connect_account_status": "active",
  "total_earnings_cents": 125000,
  "lifetime_reviews_paid": 15,
  "last_payout_date": "2025-11-01",
  "last_active": "2025-11-10",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2025-11-12T09:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Researcher not found

---

### 3. Update Researcher
**PATCH** `/admin/researchers/{researcher_id}`

Update researcher account status (suspend/activate).

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Request Body:**
```json
{
  "is_active": false,
  "suspension_reason": "Violation of platform terms of service"
}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Dr. Alan Turing",
  "email": "turing@stanford.edu",
  ...
}
```

---

### 4. Platform Statistics
**GET** `/admin/stats`

Get comprehensive platform statistics and health metrics.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Response:** `200 OK`
```json
{
  "total_users": 1247,
  "active_users_30d": 892,
  "total_researchers": 356,
  "active_researchers_30d": 234,
  "total_subscriptions": 892,
  "active_subscriptions": 765,
  "total_reviews_completed": 1543,
  "reviews_completed_30d": 187,
  "total_revenue_cents": 8920000,
  "revenue_30d_cents": 765000,
  "total_payouts_cents": 4560000,
  "payouts_30d_cents": 385000,
  "avg_review_time_days": 18.5,
  "platform_health_score": 87.5
}
```

**Platform Health Score** (0-100):
- 25 points: User activity rate (active users / total users)
- 25 points: Researcher activity rate
- 25 points: Subscription retention rate
- 25 points: Review time efficiency (inverse of avg review time)

---

### 5. Revenue Analytics
**GET** `/admin/revenue`

Get detailed revenue analytics and financial metrics.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Query Parameters:**
- `months` (int, default: 12, max: 24) - Number of months to include

**Response:** `200 OK`
```json
{
  "total_lifetime_revenue_cents": 8920000,
  "total_lifetime_payouts_cents": 4560000,
  "net_revenue_cents": 4360000,
  "current_month_revenue_cents": 765000,
  "current_month_payouts_cents": 385000,
  "revenue_by_month": [
    {
      "month": "2024-12",
      "revenue_cents": 680000,
      "payouts_cents": 340000,
      "net_cents": 340000
    },
    {
      "month": "2025-01",
      "revenue_cents": 725000,
      "payouts_cents": 362500,
      "net_cents": 362500
    }
  ],
  "top_contributors": [
    {
      "email": "researcher@stanford.edu",
      "name": "Dr. Sarah Chen",
      "total_contributed_cents": 120000
    }
  ],
  "subscription_breakdown": {
    "active": 765,
    "cancelled": 87,
    "past_due": 12
  }
}
```

---

### 6. Create Payout Pool
**POST** `/admin/payout-pool/create`

Create a new monthly payout pool.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Request Body:**
```json
{
  "pool_month": "2025-12-01",
  "initial_contribution_cents": 50000000
}
```

**Validation:**
- `pool_month` must be the first day of a month (YYYY-MM-01)
- Only one pool can exist per month

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "pool_month": "2025-12-01",
  "total_contributions_cents": 50000000,
  "total_distributed_cents": 0,
  "remaining_cents": 50000000,
  "total_reviews_assigned": 0,
  "total_reviews_completed": 0,
  "total_reviews_approved": 0,
  "payout_per_review_cents": null,
  "status": "open",
  "calculated_at": null,
  "distributed_at": null,
  "created_at": "2025-11-12T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid pool_month or pool already exists

---

### 7. Distribute Payout Pool
**PATCH** `/admin/payout-pool/{pool_id}/distribute`

Calculate and distribute funds from a payout pool to reviewers.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Request Body:**
```json
{
  "dry_run": false
}
```

**Query Parameters:**
- `dry_run` (boolean, default: false) - Calculate without executing transfers

**Response:** `200 OK`
```json
{
  "pool_id": "550e8400-e29b-41d4-a716-446655440000",
  "pool_month": "2025-11-01",
  "status": "distributed",
  "total_pool_cents": 50000000,
  "total_distributed_cents": 45000000,
  "remaining_cents": 5000000,
  "reviews_approved": 150,
  "reviewers_paid": 42,
  "payout_per_review_cents": 300000,
  "successful_transfers": 42,
  "failed_transfers": 0,
  "distribution_details": [
    {
      "reviewer_id": "...",
      "reviewer_name": "Dr. Alan Turing",
      "reviews_approved": 5,
      "payout_cents": 1500000,
      "transfer_status": "succeeded",
      "stripe_transfer_id": "tr_xxxxxxxxxxxxx"
    }
  ],
  "errors": [],
  "dry_run": false,
  "calculated_at": "2025-11-12T10:00:00Z"
}
```

**Distribution Logic:**
1. Count approved reviews in pool period
2. Calculate payout per review: `total_pool / approved_reviews`
3. Create Stripe Connect transfers for each reviewer
4. Update pool status to "distributed"

**Error Responses:**
- `404 Not Found` - Pool not found
- `400 Bad Request` - Pool already distributed or closed
- `500 Internal Server Error` - Distribution failed

---

### 8. Get Admin Action Logs
**GET** `/admin/actions`

Get audit trail of admin actions with filtering.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Query Parameters:**
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 50, max: 100) - Results per page
- `action_type` (string) - Filter by action type
- `admin_email` (string) - Filter by admin email
- `start_date` (datetime) - Filter actions after date
- `end_date` (datetime) - Filter actions before date

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "admin_id": "admin-user-id",
    "admin_email": "admin@academic-platform.com",
    "action_type": "payout_distributed",
    "target_type": "payout_pool",
    "target_id": "pool-id",
    "target_identifier": "2025-11",
    "description": "Distributed payout pool for 2025-11",
    "previous_values": {},
    "new_values": {
      "total_distributed_cents": 45000000,
      "reviewers_paid": 42
    },
    "action_metadata": {},
    "performed_at": "2025-11-12T10:00:00Z"
  }
]
```

**Action Types:**
- `user_created`, `user_updated`, `user_suspended`, `user_activated`
- `researcher_updated`, `researcher_suspended`, `researcher_activated`
- `payout_pool_created`, `payout_distributed`, `payout_pool_closed`
- `subscription_cancelled`, `subscription_refunded`
- `content_moderated`, `review_approved`, `review_rejected`
- `system_config_changed`, `permissions_changed`

---

## Authentication & Authorization

### JWT Token Structure

**Access Token Payload:**
```json
{
  "sub": "user-id-uuid",
  "email": "user@example.com",
  "role": "RESEARCHER",
  "type": "access",
  "exp": 1700000000,
  "iat": 1699998200
}
```

**Token Lifetimes:**
- Access Token: 30 minutes (configurable)
- Refresh Token: 7 days

### Role-Based Access Control

**User Roles:**
- `ADMIN` - Full platform access, can manage users and view analytics
- `EDITOR` - Can edit and approve content
- `RESEARCHER` - Can create and manage own projects
- `REVIEWER` - Can review and comment on projects
- `VIEWER` - Read-only access

**Endpoint Access:**
- `/auth/*` - Public (except /me which requires authentication)
- `/admin/*` - ADMIN role required
- All other endpoints - Authentication required, specific roles may be enforced

---

## Rate Limiting

- **Authenticated users**: 100 requests per minute
- **Unauthenticated users**: 20 requests per minute
- **Admin endpoints**: 100 requests per minute

Rate limit headers included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700000000
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful request with no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Example Usage

### Complete Authentication Flow

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register new user
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "researcher@university.edu",
        "password": "SecurePass123!",
        "full_name": "Dr. Jane Smith",
        "institution": "Stanford University"
    }
)
user = register_response.json()
print(f"Registered user: {user['email']}")

# 2. Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": "researcher@university.edu",
        "password": "SecurePass123!"
    }
)
tokens = login_response.json()
access_token = tokens["access_token"]

# 3. Get current user
headers = {"Authorization": f"Bearer {access_token}"}
me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
current_user = me_response.json()
print(f"Current user: {current_user['full_name']}")

# 4. Make authenticated requests
# ... use headers with all subsequent requests
```

### Admin Dashboard Stats

```python
# Admin login
admin_login = requests.post(
    f"{BASE_URL}/auth/admin-login",
    data={
        "username": "admin@academic-platform.com",
        "password": "Admin123!"
    }
)
admin_token = admin_login.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# Get platform stats
stats = requests.get(f"{BASE_URL}/admin/stats", headers=admin_headers).json()
print(f"Platform health: {stats['platform_health_score']}/100")
print(f"Active users (30d): {stats['active_users_30d']}")

# Get revenue analytics
revenue = requests.get(
    f"{BASE_URL}/admin/revenue?months=6",
    headers=admin_headers
).json()
print(f"Net revenue: ${revenue['net_revenue_cents']/100:.2f}")

# List researchers
researchers = requests.get(
    f"{BASE_URL}/admin/researchers?min_h_index=30&limit=10",
    headers=admin_headers
).json()
print(f"Found {len(researchers)} researchers with h-index >= 30")
```

---

## Seed Data (Development)

**Master Admin Accounts:**
- Email: `admin@academic-platform.com` / Password: `Admin123!`
- Email: `master@meta-analysis.com` / Password: `MasterAdmin2024!`

**Test Users:**
- Researcher: `researcher@stanford.edu` / `Research123!`
- Editor: `editor@nature.com` / `Editor123!`
- Reviewer: `reviewer@mit.edu` / `Review123!`

---

## WebSocket Support (Future)

Real-time updates for:
- Payout distribution progress
- Review status changes
- Platform metrics updates

---

## API Versioning

Current version: `v1`

All endpoints are prefixed with `/api/v1/`

Future versions will be released as `/api/v2/`, etc., with backward compatibility maintained.
