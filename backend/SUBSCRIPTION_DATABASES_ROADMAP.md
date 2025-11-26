# Roadmap: Adding Subscription & Specialized Databases

## Executive Summary

**Current Status:** 8 FREE databases implemented (1+ billion records)
**Goal:** Add 10+ subscription/specialized databases for comprehensive coverage
**Timeline:** Phased approach based on priority and API availability

---

## Phase 1: High Priority - No API Key Required ✅

### **ERIC (Education Resources Information Center)**
- **Status:** Can add NOW (free API)
- **Coverage:** 1.7M education records
- **API:** Free REST API
- **Effort:** LOW (2-3 hours)
- **Priority:** HIGH - fills education gap
- **Action:** Add in next deployment

---

## Phase 2: Google Scholar Integration 🔥

### **Challenge:** No Official API

Google Scholar does NOT provide an official API. Scraping is against their ToS. We have 3 options:

#### **Option 1: SerpApi (Recommended)** 💰
- **Service:** https://serpapi.com/google-scholar-api
- **Cost:** $50/month (100 searches/month)
- **Pro:** Legal, reliable, well-maintained
- **Con:** Recurring cost
- **Integration effort:** MEDIUM (4-6 hours)

**Usage example:**
```python
from serpapi import GoogleSearch

params = {
    "engine": "google_scholar",
    "q": "mindfulness meditation anxiety",
    "api_key": "YOUR_API_KEY"
}

search = GoogleSearch(params)
results = search.get_dict()
```

#### **Option 2: ScraperAPI** 💰
- **Service:** https://www.scraperapi.com/
- **Cost:** $49/month (100K requests)
- **Pro:** More affordable for volume
- **Con:** Still requires scraping approach
- **Integration effort:** MEDIUM (5-7 hours)

#### **Option 3: scholarly (Python Package)** ⚠️
- **Package:** https://github.com/scholarly-python-package/scholarly
- **Cost:** FREE
- **Pro:** No cost
- **Con:** Against Google ToS, may break, rate limits
- **Integration effort:** LOW (2-3 hours)
- **Risk:** HIGH - account bans, legal issues

**Recommendation:** Use SerpApi for production. It's worth $50/month for 389M+ paper coverage.

---

## Phase 3: Citation Tracking Databases (Require Institutional Access)

### **Scopus (Elsevier)** 🏛️
- **Coverage:** 84M+ records, excellent citation data
- **API:** https://dev.elsevier.com/
- **Cost:** Requires institutional subscription ($5000+/year)
- **Key requirement:** Institutional API key
- **Integration effort:** MEDIUM (5-7 hours)
- **Priority:** HIGH - gold standard for sciences
- **Action:** Need institutional partnership or user-provided keys

**Implementation approach:**
```python
# User provides their own Scopus API key
settings.SCOPUS_API_KEY = user_provided_key
```

### **Web of Science (Clarivate)** 🏛️
- **Coverage:** 90M+ records, best citation tracking
- **API:** https://developer.clarivate.com/apis/wos
- **Cost:** Requires institutional subscription ($10,000+/year)
- **Key requirement:** Institutional access token
- **Integration effort:** HIGH (7-10 hours)
- **Priority:** HIGH - gold standard for all disciplines
- **Action:** Need institutional partnership or user-provided keys

---

## Phase 4: Domain-Specific Databases

### **IEEE Xplore** 🔌
- **Coverage:** 5M+ computer science/engineering papers
- **API:** https://developer.ieee.org/
- **Cost:** $99/year (personal) or institutional
- **Integration effort:** MEDIUM (4-6 hours)
- **Priority:** MEDIUM - critical for CS/engineering research
- **Action:** Can implement with user API keys

### **JSTOR** 📚
- **Coverage:** 12M+ humanities/social sciences articles
- **API:** Limited API, mostly for metadata
- **Cost:** Institutional subscription
- **Integration effort:** MEDIUM (5-7 hours)
- **Priority:** MEDIUM - important for humanities
- **Action:** Need institutional partnership

### **ScienceDirect (Elsevier)** 🧪
- **Coverage:** 18M+ science/health articles
- **API:** https://dev.elsevier.com/
- **Cost:** Requires institutional subscription
- **Integration effort:** MEDIUM (5-7 hours)
- **Priority:** MEDIUM - large publisher
- **Action:** Can share API key infrastructure with Scopus

### **PsycINFO (APA)** 🧠
- **Coverage:** 5M+ psychology records
- **API:** Requires APA PsycNET subscription
- **Cost:** $1000+/year institutional
- **Integration effort:** HIGH (complex API)
- **Priority:** LOW - specialized domain
- **Action:** Low priority unless psychology-focused

### **Cochrane Library** 🏥
- **Coverage:** Systematic reviews for healthcare
- **API:** Limited, some free access
- **Cost:** Mixed (some free, some subscription)
- **Integration effort:** MEDIUM (5-7 hours)
- **Priority:** MEDIUM - gold standard for healthcare meta-analysis
- **Action:** Can implement free tier first

### **ResearchGate** 👥
- **Coverage:** 160M+ publications
- **API:** NO OFFICIAL API
- **Status:** Social network for researchers
- **Challenge:** No API access, scraping against ToS
- **Priority:** LOW - not a primary database
- **Action:** Not recommended

---

## Implementation Strategy

### **Recommended Approach:**

#### **Immediate (This Month):**
1. ✅ DONE: Add 4 free databases (DOAJ, Semantic Scholar, Crossref, BASE)
2. ✅ DONE: Fix abstract fetching
3. ⏳ Add ERIC (free, education)

#### **Short-term (Next 1-2 Months):**
4. Add Google Scholar via SerpApi ($50/month) 🔥
5. Implement "bring your own API key" system for Scopus/Web of Science
6. Add IEEE Xplore with user API keys

#### **Medium-term (3-6 Months):**
7. Partner with institutions for Scopus/Web of Science access
8. Add ScienceDirect (share Elsevier key with Scopus)
9. Add Cochrane Library (free tier)

#### **Long-term (6-12 Months):**
10. Add JSTOR if institutional access available
11. Add PsycINFO if specialized need
12. Explore pre-print servers (bioRxiv, medRxiv, SSRN)

---

## "Bring Your Own API Key" System

For subscription databases, implement a system where users can provide their own API keys:

```python
# Database model
class UserAPIKey(Base):
    user_id = Column(UUID, ForeignKey("users.id"))
    database_name = Column(String)  # "scopus", "web_of_science", etc.
    api_key = Column(String, encrypted=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime)

# Usage
if user.has_api_key("scopus"):
    results = await search_scopus(query, user.get_api_key("scopus"))
else:
    # Skip Scopus for this user
    pass
```

**Benefits:**
- Users with institutional access can use their own keys
- No platform subscription costs
- Flexible database selection per user
- Meets compliance requirements

---

## Cost Analysis

### **Free Databases (Current):**
- PubMed, arXiv, Europe PMC, CORE, DOAJ, Semantic Scholar, Crossref, BASE
- **Cost:** $0/month
- **Coverage:** 1+ billion records ✅

### **If Adding All Paid Services:**
- Google Scholar (SerpApi): $50/month
- Scopus: Requires institutional ($5000+/year)
- Web of Science: Requires institutional ($10,000+/year)
- IEEE Xplore: $99/year
- **Estimated total with BYOK:** $50/month + $99/year = ~$60/month

### **Recommended for Medical-Grade Meta-Analysis:**

**Tier 1 (Basic - FREE):**
- Current 8 databases
- Covers: Medicine, sciences, open access
- **Cost:** $0
- **Suitable for:** Most meta-analyses

**Tier 2 (Professional - $50/month):**
- Tier 1 + Google Scholar (via SerpApi)
- **Cost:** $50/month
- **Suitable for:** Comprehensive multidisciplinary research

**Tier 3 (Enterprise - BYOK):**
- Tier 2 + Scopus + Web of Science + IEEE (user keys)
- **Cost:** $50/month + user institutional access
- **Suitable for:** Academic/institutional research with citation tracking

---

## Next Actions

1. **Immediate:** Add ERIC database (free)
2. **Discuss:** Budget approval for Google Scholar SerpApi ($50/month)
3. **Design:** "Bring Your Own API Key" system
4. **Document:** User guide for institutional API key setup
5. **Test:** Run meta-analysis with 9 databases (8 current + ERIC)

---

**Last Updated:** November 25, 2025
**Status:** 8 databases live, roadmap for 10+ more
**Recommendation:** Proceed with SerpApi for Google Scholar access
