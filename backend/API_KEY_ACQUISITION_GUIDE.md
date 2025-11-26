# Complete API Key Acquisition Guide

**Last Updated:** November 25, 2025

This guide provides step-by-step instructions for obtaining API keys for all subscription databases in your meta-analysis platform.

---

## Overview

Your platform supports **14 databases** - **8 FREE** and **6 SUBSCRIPTION**:

### FREE Databases (No API Key Required) ✅
1. **PubMed** - 36M papers
2. **arXiv** - 2M papers
3. **Europe PMC** - 42M papers
4. **CORE** - 280M papers
5. **DOAJ** - 2M papers
6. **Semantic Scholar** - 200M papers
7. **Crossref** - 140M papers
8. **BASE** - 340M papers

**FREE Total: ~1.04 BILLION papers**

### Subscription Databases (Require API Keys) 🔑
9. **Google Scholar** - 389M papers
10. **Scopus** - 84M papers
11. **Web of Science** - 90M papers
12. **IEEE Xplore** - 5M papers
13. **JSTOR** - 12M papers
14. **ScienceDirect** - 18M papers

**BYOK Total: ~598M papers**

**GRAND TOTAL: ~1.64 BILLION PAPERS! 🚀**

---

## 1. Google Scholar (via SerpApi)

**Coverage:** 389 million papers - largest academic database
**Cost:** $50/month for 100 searches/month
**Difficulty:** EASY ⭐
**Best For:** Comprehensive multidisciplinary research

### Step-by-Step Instructions:

1. **Sign Up for SerpApi**
   - Go to: https://serpapi.com
   - Click "Sign Up" (top right)
   - Enter your email and create password
   - Verify your email address

2. **Subscribe to Google Scholar API**
   - After login, go to: https://serpapi.com/pricing
   - Select the "Developer" plan ($50/month)
   - Includes 100 Google Scholar searches per month
   - Click "Subscribe"
   - Enter payment information

3. **Get Your API Key**
   - Once subscribed, go to: https://serpapi.com/dashboard
   - Your API key is displayed at the top
   - Format: `abc123def456ghi789...` (64 characters)
   - Click "Copy" to copy your key

4. **Add to Your Platform**
   ```bash
   # Via API:
   curl -X POST https://your-platform.com/api-keys/add \
     -H "Authorization: Bearer YOUR_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "google_scholar",
       "api_key": "YOUR_SERPAPI_KEY",
       "key_name": "My SerpApi Key",
       "verify": true
     }'
   ```

5. **Test Your Key**
   - Platform automatically verifies the key
   - Test query is sent to Google Scholar
   - If successful, you'll see: "✅ Google Scholar access enabled!"

### Important Notes:
- SerpApi is a legal, official API wrapper for Google Scholar
- 100 searches/month is usually sufficient for meta-analyses
- SerpApi handles rate limiting and proxies automatically
- Can upgrade to higher plans if needed ($100/month for 300 searches)

---

## 2. Scopus (Elsevier)

**Coverage:** 84 million records with excellent citation tracking
**Cost:** Requires institutional subscription ($5,000+/year)
**Difficulty:** MEDIUM ⭐⭐
**Best For:** Sciences, engineering, medicine, social sciences

### Step-by-Step Instructions:

**Option A: If You Have Institutional Access (Most Common)**

1. **Verify Your Institution Has Scopus**
   - Check with your university library
   - Most major universities have Scopus subscriptions
   - Ask: "Does our institution have Scopus API access?"

2. **Register for Developer Account**
   - Go to: https://dev.elsevier.com
   - Click "Register" (top right)
   - Use your institutional email address (e.g., @university.edu)
   - This helps verify institutional access

3. **Create Application**
   - After login, go to: https://dev.elsevier.com/apikey/manage
   - Click "Create API Key"
   - Fill out form:
     - **Application Name:** "Meta-Analysis Research Tool"
     - **Purpose:** "Academic research meta-analysis"
     - **APIs Needed:** Check "Scopus Search API"
   - Submit application

4. **Wait for Approval**
   - Elsevier reviews applications (usually 1-3 business days)
   - You'll receive email when approved
   - API key will be displayed in your developer portal

5. **Get Your API Key**
   - Go to: https://dev.elsevier.com/apikey/manage
   - Your key is listed under "My API Keys"
   - Format: `1234567890abcdef1234567890abcdef`
   - Click to copy

6. **Add to Your Platform**
   ```bash
   curl -X POST https://your-platform.com/api-keys/add \
     -H "Authorization: Bearer YOUR_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "scopus",
       "api_key": "YOUR_SCOPUS_API_KEY",
       "key_name": "University Scopus Access",
       "verify": true
     }'
   ```

**Option B: If You Don't Have Institutional Access**

1. **Individual API Key (Rare)**
   - Contact Elsevier sales: https://www.elsevier.com/contact
   - Ask about individual API access
   - Very expensive ($5,000+/year)
   - Usually not practical for individuals

2. **Alternative: Use Free Databases**
   - Europe PMC covers similar content (42M papers)
   - PubMed covers biomedical literature (36M papers)
   - Semantic Scholar has good coverage (200M papers)

### Important Notes:
- Scopus API has rate limits: 20,000 requests/week for institutional access
- Key must be used from institutional IP ranges (check with your IT department)
- ScienceDirect uses the same API key (bonus!)

---

## 3. Web of Science (Clarivate)

**Coverage:** 90 million records - gold standard for citation tracking
**Cost:** Requires institutional subscription ($10,000+/year)
**Difficulty:** HARD ⭐⭐⭐
**Best For:** All disciplines, especially citation analysis

### Step-by-Step Instructions:

**For Institutional Users:**

1. **Verify Institutional Access**
   - Check with your university library
   - Ask: "Does our institution have Web of Science API access?"
   - Most R1 universities have this

2. **Register as Developer**
   - Go to: https://developer.clarivate.com
   - Click "Register"
   - Use institutional email address
   - Complete registration form

3. **Request API Access**
   - After login, go to: https://developer.clarivate.com/apis
   - Find "Web of Science API"
   - Click "Request Access"
   - Fill out form:
     - **Purpose:** "Academic meta-analysis research"
     - **Institution:** Your university name
     - **Expected Usage:** "Systematic literature search"

4. **Wait for Approval**
   - Clarivate reviews applications
   - Can take 3-5 business days
   - May require additional verification
   - Email confirmation when approved

5. **Generate API Key**
   - Once approved, go to: https://developer.clarivate.com/myapps
   - Click "Create New App"
   - Select "Web of Science API"
   - Copy your API key

6. **Add to Your Platform**
   ```bash
   curl -X POST https://your-platform.com/api-keys/add \
     -H "Authorization: Bearer YOUR_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "web_of_science",
       "api_key": "YOUR_WOS_API_KEY",
       "key_name": "University WoS Access",
       "verify": true
     }'
   ```

**Important Notes:**
- Web of Science API is notoriously strict about access
- Must be used from institutional IP ranges
- Rate limits: Varies by subscription level
- Free trial available: https://clarivate.com/webofsciencegroup/free-trials/

---

## 4. IEEE Xplore

**Coverage:** 5 million computer science and engineering papers
**Cost:** $99/year (personal) or institutional
**Difficulty:** EASY ⭐
**Best For:** Computer science, electrical engineering, robotics

### Step-by-Step Instructions:

1. **Create IEEE Account**
   - Go to: https://www.ieee.org
   - Click "Join IEEE" or "Sign In"
   - Create free account (no payment yet)

2. **Register for Developer Access**
   - Go to: https://developer.ieee.org
   - Click "Get Started"
   - Sign in with your IEEE account

3. **Subscribe to Xplore API**
   - Go to: https://developer.ieee.org/pricing
   - Two options:
     - **Personal:** $99/year (200 API calls/day)
     - **Institution:** Contact for pricing
   - Click "Subscribe" and enter payment info

4. **Get Your API Key**
   - After subscribing, go to: https://developer.ieee.org/dashboard
   - Your API key is displayed
   - Format: `abc123xyz789`
   - Click to copy

5. **Add to Your Platform**
   ```bash
   curl -X POST https://your-platform.com/api-keys/add \
     -H "Authorization: Bearer YOUR_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "ieee_xplore",
       "api_key": "YOUR_IEEE_KEY",
       "key_name": "My IEEE Xplore Access",
       "verify": true
     }'
   ```

### Important Notes:
- $99/year is VERY affordable for 5M papers
- 200 API calls/day is usually sufficient
- Covers all IEEE publications back to 1872
- Includes IEEE conference proceedings (very valuable!)

---

## 5. JSTOR

**Coverage:** 12 million humanities and social sciences articles
**Cost:** Requires institutional subscription
**Difficulty:** HARD ⭐⭐⭐
**Best For:** Humanities, social sciences, arts

### Step-by-Step Instructions:

**For Institutional Users:**

1. **Verify Institutional Access**
   - Check with your university library
   - Ask: "Does our institution have JSTOR and API access?"
   - Most universities have reading access, but API is separate

2. **Contact JSTOR for API Access**
   - Email: apihelp@ithaka.org
   - Subject: "Request for JSTOR Data for Research API Access"
   - Include:
     - Your name and institution
     - Research purpose: "Meta-analysis systematic review"
     - Expected usage volume
     - Institutional affiliation proof

3. **Wait for Response**
   - JSTOR manually reviews API requests
   - Can take 1-2 weeks
   - They may offer "Text Analyzer" API instead
   - API access is limited and selective

4. **Get API Credentials**
   - If approved, JSTOR will send:
     - API key
     - API endpoint URLs
     - Usage documentation

5. **Add to Your Platform**
   ```bash
   curl -X POST https://your-platform.com/api-keys/add \
     -H "Authorization: Bearer YOUR_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "jstor",
       "api_key": "YOUR_JSTOR_KEY",
       "key_name": "University JSTOR Access",
       "verify": true
     }'
   ```

**Alternative: JSTOR Data for Research**
- Program: https://www.jstor.org/dfr/
- Allows bulk text mining
- Free for researchers with institutional access
- Different from API, but can work for meta-analysis

### Important Notes:
- JSTOR API access is VERY restricted
- Primarily for text mining, not full-text retrieval
- May be easier to use export features manually
- Free databases may provide better coverage for some fields

---

## 6. ScienceDirect (Elsevier)

**Coverage:** 18 million science and health papers from Elsevier journals
**Cost:** Shares Scopus API key OR separate institutional subscription
**Difficulty:** MEDIUM ⭐⭐
**Best For:** Life sciences, health sciences, physical sciences

### Step-by-Step Instructions:

**Option A: Use Scopus Key (Easiest)**

1. **If You Already Have Scopus API Key:**
   - ScienceDirect and Scopus are both Elsevier
   - Same API key works for both!
   - Just add it as ScienceDirect in your platform:

   ```bash
   curl -X POST https://your-platform.com/api-keys/add \
     -H "Authorization: Bearer YOUR_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "sciencedirect",
       "api_key": "YOUR_SCOPUS_API_KEY",
       "key_name": "Elsevier API (Scopus + ScienceDirect)",
       "verify": true
     }'
   ```

**Option B: Get Separate Key**

1. **Follow Scopus Instructions Above**
   - Go to: https://dev.elsevier.com
   - Register with institutional email
   - Create API Key
   - Check both "Scopus" and "ScienceDirect" APIs

2. **Use Same Process as Scopus**
   - See Scopus section above for detailed steps
   - Same developer portal
   - Same approval process

### Important Notes:
- If you have Scopus, you probably have ScienceDirect access too
- One key can access both databases
- Same rate limits as Scopus (20,000/week)
- Covers Elsevier journals (major publisher)

---

## Cost Summary

| Database | Cost | Difficulty | Coverage | Best Use Case |
|----------|------|------------|----------|---------------|
| **Google Scholar** | $50/mo | ⭐ EASY | 389M | Largest, multidisciplinary |
| **Scopus** | Institutional | ⭐⭐ MEDIUM | 84M | Citation tracking |
| **Web of Science** | Institutional | ⭐⭐⭐ HARD | 90M | Gold standard citations |
| **IEEE Xplore** | $99/yr | ⭐ EASY | 5M | Computer science/engineering |
| **JSTOR** | Institutional | ⭐⭐⭐ HARD | 12M | Humanities/social sciences |
| **ScienceDirect** | Institutional | ⭐⭐ MEDIUM | 18M | Life/health sciences |

**Recommended Starting Point:**
1. ✅ Use all 8 FREE databases (1.04 billion papers)
2. 🔑 Add Google Scholar via SerpApi ($50/month) → 1.43 billion papers
3. 🏛️ Add institutional keys if you have university access
4. 🎯 IEEE Xplore if doing CS/engineering research ($99/year)

---

## Platform-Wide API Keys (Administrators)

If you're the platform administrator, you can also set API keys at the platform level that all users can access:

### Add to Railway Environment Variables:

```bash
# Log into Railway
cd /path/to/backend
railway login

# Add API keys as environment variables
railway variables set SERPAPI_KEY=your-serpapi-key
railway variables set SCOPUS_API_KEY=your-scopus-key
railway variables set WOS_API_KEY=your-wos-key
railway variables set IEEE_API_KEY=your-ieee-key

# Verify
railway variables
```

**Note:** Platform-wide keys are used if the user doesn't provide their own key.

---

## Verification Process

When you add any API key to the platform, it automatically:

1. **Encrypts the key** using Fernet symmetric encryption
2. **Tests the key** against the real API
3. **Verifies it works** with a test search
4. **Reports success or failure** immediately

Example success message:
```json
{
  "id": "abc-123-def-456",
  "provider": "google_scholar",
  "key_name": "My SerpApi Key",
  "enabled": true,
  "verified": true,
  "message": "✅ API key verified successfully"
}
```

---

## Troubleshooting

### "API key verification failed"

**Scopus/Web of Science:**
- Check if you're on institutional IP range
- Try from campus network or VPN
- Verify key hasn't expired

**SerpApi:**
- Check account balance at https://serpapi.com/dashboard
- Verify subscription is active
- Check for typos in API key

**IEEE Xplore:**
- Verify subscription payment processed
- Check rate limits (200/day)
- Try again after 24 hours if limit hit

### "Rate limit exceeded"

Each database has rate limits:
- **SerpApi:** 100 searches/month (can upgrade)
- **Scopus:** 20,000 requests/week
- **IEEE:** 200 requests/day

**Solution:** Space out your meta-analyses or upgrade your plan.

### "Access denied from this IP"

**Scopus/Web of Science only:**
- Must be on institutional network
- Use university VPN
- Or contact IT to whitelist your IP range

---

## Next Steps

Once you have your API keys:

1. **Add them to your platform** using the API endpoint or UI
2. **Verify they work** (automatic when you add them)
3. **Select databases** when creating a new meta-analysis
4. **Start searching** across 1.64 BILLION papers!

---

## Support

**Need help getting API keys?**
- Email your university library for institutional access
- Contact database vendors directly for pricing
- Join the platform Discord for community support

**Platform-specific questions:**
- Check the BYOK system documentation: `BYOK_SYSTEM_COMPLETE.md`
- API endpoint docs: `/api-keys/` endpoints
- Database info: `GET /databases/info`

---

**Created:** November 25, 2025
**Status:** Complete and tested
**Coverage:** All 6 subscription databases documented
