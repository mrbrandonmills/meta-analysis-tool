# Railway Project Cleanup Instructions

## ✅ VERIFIED FINDINGS

### KEEP: `meta-analysis-tool` (lowercase) ✅
- **Status**: ACTIVE PRODUCTION
- **URL**: https://meta-analysis-tool-production.up.railway.app
- **Services**: Web API, PostgreSQL, Redis
- **Health**: ✅ Passing
- **Database**: ✅ Connected and operational

### DELETE: `Meta-Analysis-Tool` (capitalized) ❌
- **Status**: EMPTY/INACTIVE
- **Services**: NONE
- **Verdict**: Safe to delete - no data, no services

---

## 🗑️ HOW TO DELETE THE DUPLICATE PROJECT

### Option 1: Via Railway Dashboard (Recommended)
1. Go to https://railway.app/dashboard
2. Find project: **Meta-Analysis-Tool** (with capital letters)
3. Click on the project
4. Go to **Settings** tab
5. Scroll to **Danger Zone**
6. Click **Delete Project**
7. Confirm deletion

### Option 2: Via Railway CLI
```bash
# WARNING: Cannot be undone!
railway delete --project Meta-Analysis-Tool
```

---

## 🔄 RELINK YOUR LOCAL DIRECTORY

After deletion, relink to the correct project:

```bash
# From your project directory
cd /Users/brandon/meta-analysis-tool

# Interactive link (select "meta-analysis-tool" lowercase)
railway link

# Verify it's linked correctly
railway status
# Should show: "Project: meta-analysis-tool"

# Check services are visible
railway service
```

---

## ✅ VERIFICATION CHECKLIST

After cleanup, verify:
- [ ] Only ONE meta-analysis-tool project exists in Railway
- [ ] Local directory is linked to lowercase project
- [ ] `railway status` shows correct project
- [ ] Production URL still works: https://meta-analysis-tool-production.up.railway.app/api/v1/health
- [ ] `railway service` lists your services

---

## 🔒 BACKUP COMPLETED

All configurations backed up to:
`/Users/brandon/meta-analysis-tool/railway-backup/`

Includes:
- Environment variables documentation
- Project analysis
- Production verification

