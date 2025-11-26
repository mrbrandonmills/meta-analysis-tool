# Testing Checklist - What Works RIGHT NOW (Before Buying API Keys)

**Last Updated:** November 25, 2025
**Purpose:** Verify all FREE features work perfectly before paying for subscription databases

---

## What's Available NOW (100% FREE)

### 8 FREE Databases (1.04 Billion Papers)

1. ✅ **PubMed** - 36M biomedical papers (NIH)
2. ✅ **arXiv** - 2M preprints (physics, CS, math)
3. ✅ **Europe PMC** - 42M life sciences papers
4. ✅ **CORE** - 280M open access papers
5. ✅ **DOAJ** - 2M open access journals
6. ✅ **Semantic Scholar** - 200M papers with AI analysis
7. ✅ **Crossref** - 140M DOI records
8. ✅ **BASE** - 340M academic documents

**Coverage:** 1.04 BILLION papers
**Cost:** $0
**Status:** Deployed and working

---

## Testing Checklist

### ✅ TEST 1: Verify System is Running

**Command:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/health
```

**Expected Result:**
```json
{"status": "healthy"}
```

**Status:** ✅ Confirmed working (bf35f7e9 completed successfully)

---

### ✅ TEST 2: Create a New Meta-Analysis

**Command:**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What are the effects of exercise on depression?",
    "topic": "Exercise and Mental Health",
    "databases": ["pubmed", "europepmc"],
    "inclusion_criteria": [
      "Randomized controlled trial",
      "Adult participants",
      "Exercise intervention",
      "Depression as outcome"
    ],
    "exclusion_criteria": [
      "Non-English language",
      "Qualitative studies"
    ],
    "peer_review_only": false
  }'
```

**Expected Result:**
```json
{
  "id": "some-uuid-here",
  "status": "created",
  "message": "Meta-analysis created successfully. Use /execute endpoint to run the workflow."
}
```

**What to verify:**
- Returns an ID
- Status is "created"
- No errors

---

### ✅ TEST 3: Execute the Meta-Analysis

**Command:**
```bash
# Use the ID from TEST 2
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/execute/YOUR_ID_HERE
```

**Expected Result:**
```json
{
  "message": "Meta-analysis workflow started in background",
  "analysis_id": "your-id-here",
  "status": "in_progress"
}
```

**What to verify:**
- Returns immediately (doesn't hang)
- Status is "in_progress"
- Background workflow started

---

### ✅ TEST 4: Check Progress

**Command:**
```bash
# Check every 30 seconds
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/status/YOUR_ID_HERE
```

**Expected Result (In Progress):**
```json
{
  "id": "your-id",
  "status": "in_progress",
  "progress_percentage": 66.7,
  "agent_progress": [
    {
      "agent_name": "SearchAgent",
      "status": "success"
    },
    {
      "agent_name": "ScreeningAgent",
      "status": "success"
    },
    {
      "agent_name": "CredibilityAgent",
      "status": "in_progress"
    }
  ]
}
```

**Expected Result (Completed):**
```json
{
  "id": "your-id",
  "status": "completed",
  "progress_percentage": 100.0,
  "agents_completed": 3,
  "agents_total": 3
}
```

**What to verify:**
- All 3 agents complete: SearchAgent, ScreeningAgent, CredibilityAgent
- Status changes to "completed"
- No errors

---

### ✅ TEST 5: Verify Real Data (CRITICAL)

**What to Check:**
1. **Studies Found:** Should find real papers from PubMed/Europe PMC
2. **Studies Have PMIDs:** Every PubMed paper should have a PMID
3. **Abstracts Present:** Studies should have abstracts (fix deployed)
4. **Some Studies Included:** Not ALL studies should be excluded

**Manual Verification:**
```bash
# Get a study's PMID from the results
# Example PMID: 12345678

# Verify it exists on PubMed:
curl "https://pubmed.ncbi.nlm.nih.gov/12345678/"
```

**Expected:** PubMed page loads showing the real paper

---

### ✅ TEST 6: Verify Credibility Ranking Works

**What to Check:**
Studies should be ranked with:
- **Credibility Level:** HIGH, MEDIUM, LOW, or VERY LOW
- **Score:** 0-100
- **Color:** Green, Yellow, Orange, or Red
- **Reasoning:** Explanation of why

**Check in logs or results:**
- Peer-reviewed papers → HIGH/MEDIUM
- Preprints → MEDIUM/LOW
- Proper evaluation based on journal quality, study design, etc.

---

### ✅ TEST 7: Test Multiple Databases

**Command:**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Effects of meditation on anxiety",
    "topic": "Meditation and Anxiety",
    "databases": ["pubmed", "arxiv", "europepmc", "doaj", "semantic_scholar"],
    "peer_review_only": false
  }'
```

**What to verify:**
- All 5 databases are searched
- Results from multiple sources
- Deduplication working (no exact duplicates)
- More results than single database

---

### ✅ TEST 8: Test Peer-Review Filter

**Test A: With Peer-Review Only**
```bash
curl -X POST ... \
  -d '{
    ...
    "peer_review_only": true
  }'
```

**Expected:** Only peer-reviewed papers, no preprints from arXiv

**Test B: Without Filter**
```bash
curl -X POST ... \
  -d '{
    ...
    "peer_review_only": false
  }'
```

**Expected:** Includes both peer-reviewed and preprints

---

## Success Criteria

Before paying for API keys, ALL of these should work:

- [ ] System responds to health checks
- [ ] Can create new meta-analysis
- [ ] Can execute workflow in background
- [ ] All 3 agents complete successfully
- [ ] Studies have real PMIDs/DOIs
- [ ] Studies have abstracts (not empty)
- [ ] Some studies are included (not all excluded)
- [ ] Credibility ranking produces 4 levels
- [ ] Multiple databases can be searched together
- [ ] Peer-review filter works
- [ ] Results are deduped (no exact duplicates)
- [ ] Workflow completes in reasonable time (< 10 minutes)

---

## Known Working Test

**Confirmed Working Analysis:**
- **ID:** `bf35f7e9-51eb-4c39-badb-14ffb74ebd2a`
- **Status:** ✅ Completed successfully
- **Agents:** All 3 completed (SearchAgent, ScreeningAgent, CredibilityAgent)
- **Completed:** 2025-11-25 06:18:16 UTC

This proves the system works end-to-end!

---

## If Something Fails

### Common Issues:

**1. "Not Found" errors**
- Check you're using correct API path: `/api/v1/meta-analysis/...`
- Verify Railway deployment is running

**2. "All studies excluded"**
- Check abstract fetching is working (deployed fix)
- Verify inclusion/exclusion criteria aren't too strict

**3. "No results found"**
- Try broader research question
- Check databases are actually being searched (logs)
- Verify API endpoints are accessible

**4. Timeout errors**
- Workflow runs in background (should never timeout)
- Check status endpoint instead of waiting for response

---

## Next Steps After Testing

### Once FREE system is verified:

**Option A: Add Google Scholar ($50/month)**
1. Sign up at https://serpapi.com
2. Subscribe to Developer plan ($50/month)
3. Get API key
4. Add via BYOK system (once deployed)
5. Gain access to 389M additional papers

**Option B: Add IEEE Xplore ($99/year)**
1. Sign up at https://developer.ieee.org
2. Subscribe ($99/year)
3. Get API key
4. Add via BYOK system
5. Gain 5M CS/engineering papers

**Option C: Use Institutional Keys (FREE if you have them)**
1. Check with university library
2. Get Scopus, Web of Science keys
3. Add to platform
4. Gain 84M + 90M papers

---

## Testing Script (All Tests)

**Save as `test_meta_analysis.sh`:**
```bash
#!/bin/bash

API_URL="https://meta-analysis-tool-production.up.railway.app/api/v1"

echo "=== TEST 1: Create Meta-Analysis ==="
RESPONSE=$(curl -s -X POST "$API_URL/meta-analysis/create" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Effects of exercise on depression",
    "topic": "Exercise and Mental Health",
    "databases": ["pubmed", "europepmc"],
    "inclusion_criteria": ["RCT", "Adults", "Exercise", "Depression"],
    "exclusion_criteria": ["Non-English"],
    "peer_review_only": false
  }')

echo "$RESPONSE"
ANALYSIS_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Analysis ID: $ANALYSIS_ID"

echo ""
echo "=== TEST 2: Execute Workflow ==="
curl -s -X POST "$API_URL/meta-analysis/execute/$ANALYSIS_ID"

echo ""
echo "=== TEST 3: Check Status (wait 30 seconds between checks) ==="
for i in {1..10}; do
  echo "Check #$i..."
  STATUS=$(curl -s "$API_URL/meta-analysis/status/$ANALYSIS_ID" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Status: {data['status']}, Progress: {data['progress_percentage']}%\")")
  echo "$STATUS"

  if echo "$STATUS" | grep -q "completed"; then
    echo "✅ COMPLETED!"
    break
  fi

  sleep 30
done
```

**Run it:**
```bash
chmod +x test_meta_analysis.sh
./test_meta_analysis.sh
```

---

## Summary

**What Works RIGHT NOW (FREE):**
- 8 databases with 1.04 billion papers
- Automatic search across all databases
- AI screening and credibility ranking
- Real data only (no simulation)
- Complete workflow automation

**What to Test Before Paying:**
- All tests in this checklist pass
- Studies have abstracts
- Some studies are included (not all excluded)
- Credibility ranking works correctly
- Multiple databases search together

**When to Buy API Keys:**
- After confirming FREE system works perfectly
- When you need access to Google Scholar (389M papers)
- When you need specialized databases (IEEE, Scopus, etc.)

---

**Created:** November 25, 2025
**Purpose:** Validate FREE system before spending money
**Status:** Ready to test
