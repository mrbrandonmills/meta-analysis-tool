# Quick Start Guide - Admin API

## Quick Setup

### 1. Database Migration
```bash
cd /Users/brandon/meta-analysis-tool/backend

# Generate migration for admin_actions table
alembic revision --autogenerate -m "Add admin_actions table for audit trail"

# Apply migration
alembic upgrade head
```

### 2. Seed Database (Development)
```bash
# This creates master admin accounts and test users
python -m app.db.seeds
```

### 3. Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Quick Test Commands

### 1. Admin Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@academic-platform.com&password=Admin123!"
```

Save the `access_token` from response.

### 2. Get Platform Stats
```bash
export TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer $TOKEN"
```

### 3. List Researchers
```bash
curl -X GET "http://localhost:8000/api/v1/admin/researchers?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Get Revenue Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/admin/revenue?months=6" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Create Payout Pool
```bash
curl -X POST http://localhost:8000/api/v1/admin/payout-pool/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pool_month": "2025-12-01",
    "initial_contribution_cents": 50000000
  }'
```

### 6. View Admin Logs
```bash
curl -X GET "http://localhost:8000/api/v1/admin/actions?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Test Credentials

### Master Admin
```
Email: admin@academic-platform.com
Password: Admin123!
```

or

```
Email: master@meta-analysis.com
Password: MasterAdmin2024!
```

### Regular Users (for testing access control)
```
Researcher: researcher@stanford.edu / Research123!
Editor: editor@nature.com / Editor123!
Reviewer: reviewer@mit.edu / Review123!
```

---

## Interactive API Documentation

Once server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Filter by "admin" tag to see all admin endpoints.

---

## Testing Checklist

### Authentication Flow
- [ ] Register new user
- [ ] Login as regular user
- [ ] Verify regular user gets 403 on admin endpoints
- [ ] Login as admin
- [ ] Verify admin can access admin endpoints

### Admin Endpoints
- [ ] GET /admin/stats
- [ ] GET /admin/revenue
- [ ] GET /admin/researchers
- [ ] GET /admin/researchers/{id}
- [ ] PATCH /admin/researchers/{id}
- [ ] POST /admin/payout-pool/create
- [ ] PATCH /admin/payout-pool/{id}/distribute (dry-run)
- [ ] GET /admin/actions

### Audit Trail
- [ ] Perform admin action
- [ ] Verify logged in admin_actions table
- [ ] Check IP address captured
- [ ] Verify before/after values

---

## Python Test Script

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Admin login
response = requests.post(
    f"{BASE_URL}/auth/admin-login",
    data={
        "username": "admin@academic-platform.com",
        "password": "Admin123!"
    }
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get platform stats
stats = requests.get(f"{BASE_URL}/admin/stats", headers=headers).json()
print(f"Platform Health: {stats['platform_health_score']}/100")
print(f"Total Users: {stats['total_users']}")
print(f"Active Researchers (30d): {stats['active_researchers_30d']}")

# Get revenue
revenue = requests.get(f"{BASE_URL}/admin/revenue", headers=headers).json()
print(f"\nNet Revenue: ${revenue['net_revenue_cents']/100:,.2f}")
print(f"Current Month: ${revenue['current_month_revenue_cents']/100:,.2f}")

# List top researchers
researchers = requests.get(
    f"{BASE_URL}/admin/researchers?limit=5&sort_by=h_index&sort_order=desc",
    headers=headers
).json()
print(f"\nTop 5 Researchers by h-index:")
for r in researchers:
    print(f"  - {r['name']}: h-index={r['h_index']}, citations={r['total_citations']}")
```

---

## Common Issues

### 1. 401 Unauthorized
- Token expired (access tokens last 30 minutes)
- Use refresh token endpoint or re-login

### 2. 403 Forbidden
- User doesn't have ADMIN role
- Use admin-login endpoint with admin credentials

### 3. 422 Validation Error
- Check request body format
- Verify required fields
- Check data types (dates must be YYYY-MM-DD)

### 4. Database Connection Error
- Verify DATABASE_URL environment variable
- Run migrations: `alembic upgrade head`

---

## File Locations

**Models:**
- `/app/models/admin_action.py` - AdminAction model

**API Routes:**
- `/app/api/v1/auth.py` - Authentication (includes admin-login)
- `/app/api/v1/admin.py` - Admin management endpoints

**Documentation:**
- `/backend/API_DOCUMENTATION.md` - Complete API docs
- `/backend/IMPLEMENTATION_SUMMARY.md` - Implementation details
- `/backend/QUICK_START_ADMIN.md` - This file

**Configuration:**
- `/app/main.py` - FastAPI app with admin router
- `/app/db/seeds.py` - Database seeding with admin accounts
- `/app/core/security.py` - JWT and RBAC

---

## Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@localhost/dbname
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional
ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_xxxxx
DEBUG=false
```

---

## Next Steps

1. **Production Deployment:**
   - Change admin passwords
   - Set strong SECRET_KEY
   - Configure CORS
   - Enable HTTPS
   - Set up monitoring

2. **Database:**
   - Run migrations
   - Set up backups
   - Configure connection pooling

3. **Security:**
   - Rotate credentials
   - Enable rate limiting
   - Review audit logs regularly
   - Set up alerting

4. **Testing:**
   - Write integration tests
   - Test all admin endpoints
   - Verify RBAC enforcement
   - Load test with sample data

---

## Support

- API Docs: http://localhost:8000/docs
- Complete Documentation: `/backend/API_DOCUMENTATION.md`
- Implementation Details: `/backend/IMPLEMENTATION_SUMMARY.md`

---

**Last Updated**: November 12, 2025
