# Tier System Integration Checklist

**Quick Reference for Backend Integration**

## ⚠️ CRITICAL: Study Before Coding

```bash
# 1. Check auth functions
grep "^async def\|^def" app/core/security.py | grep -i "user"

# 2. Check database dependency
grep "get_async_db" app/api/v1/*.py | head -3

# 3. Check existing route patterns
head -50 app/api/v1/manuscripts.py
```

## ✅ Integration Checklist

- [ ] **Studied app/core/security.py** - Know actual auth function names
- [ ] **Studied app/db/session.py** - Confirmed get_async_db exists
- [ ] **Fixed tier_applications.py imports** - Match existing patterns
- [ ] **Fixed admin/tier_applications.py imports** - Match existing patterns
- [ ] **Updated main.py** - Registered both routers
- [ ] **Tested locally** - `python3 -c "from app.api.v1 import tier_applications"`
- [ ] **Tested locally** - `uvicorn app.main:app --reload` starts without errors
- [ ] **Checked /docs** - Tier endpoints visible at http://localhost:8000/docs
- [ ] **Committed changes** - Only after local tests pass
- [ ] **Deployed to Railway** - `git push origin main`
- [ ] **Ran migration** - `railway run alembic upgrade heads`
- [ ] **Configured SMTP** - Set 7 Railway variables
- [ ] **Tested production** - Endpoints return data, not 404

## 🚨 Common Mistakes

1. ❌ Assuming function names without checking
2. ❌ Deploying before testing locally
3. ❌ Forgetting to register routes in main.py
4. ❌ Using `get_db` instead of `get_async_db`
5. ❌ Not running the database migration

## 🎯 Success Criteria

```bash
# Should return tier endpoints:
curl https://meta-analysis-tool-production.up.railway.app/openapi.json | grep tier-applications

# Should return 401 (needs auth), not 404:
curl https://meta-analysis-tool-production.up.railway.app/api/v1/tier-applications/my-applications
```

**See:** `../TIER_SYSTEM_INTEGRATION_FIX.md` for full details
