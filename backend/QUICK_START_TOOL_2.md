# Quick Start: Research Direction Finder

Get up and running with Tool 2 in 5 minutes.

## Prerequisites

- Backend server running
- Database configured
- Anthropic API key set

## Step 1: Run Migration (30 seconds)

```bash
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 006 -> 007, add research direction table
```

## Step 2: Verify Installation (10 seconds)

Check that the API is available:

```bash
curl http://localhost:8000/api/v1/health
```

Should return healthy status.

## Step 3: Test with Unit Tests (1 minute)

```bash
cd backend
python3 test_research_direction_unit.py
```

Expected output:
```
✓ PASSED: Agent Initialization
✓ PASSED: Gap Identification
✓ PASSED: Question Generation
✓ PASSED: Proposal Creation
✓ PASSED: Full Process
✓ PASSED: Helper Methods

Total: 6/6 tests passed
🎉 ALL TESTS PASSED!
```

## Step 4: Run Integration Tests (2 minutes)

```bash
cd backend
chmod +x test_research_direction.sh
./test_research_direction.sh
```

Expected output:
```
✓ Server is running
✓ User authenticated
✓ Meta-analysis created
✓ Research directions generated
✓ ALL TESTS PASSED
```

## Step 5: Make Your First API Call (1 minute)

### A. Get Auth Token

```bash
# Register or login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword"
  }'
```

Save the `access_token` from the response.

### B. Create/Complete Meta-Analysis

You need a completed meta-analysis first. Either:
- Use an existing one
- Create new one via API
- Run Tool 1 to completion

### C. Generate Research Directions

```bash
export TOKEN="your-access-token-here"
export META_ID="your-meta-analysis-id"

curl -X POST http://localhost:8000/api/v1/research-direction/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"meta_analysis_id\": \"$META_ID\",
    \"focus_areas\": [\"methodology\", \"populations\"],
    \"max_proposals\": 5,
    \"include_literature_review\": true
  }"
```

### D. View Results

```bash
curl -X GET "http://localhost:8000/api/v1/research-direction/by-meta-analysis/$META_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## ✅ Success Checklist

- [ ] Migration completed without errors
- [ ] Health check returns 200 OK
- [ ] Unit tests pass (6/6)
- [ ] Integration tests pass
- [ ] API call returns research directions
- [ ] Results include gaps, questions, proposals

---

## 🔧 Troubleshooting

### Issue: Migration fails
**Solution**: Check database connection and ensure previous migrations ran

```bash
alembic current
alembic history
```

### Issue: Tests fail with import errors
**Solution**: Activate virtual environment

```bash
source venv/bin/activate  # or your venv path
```

### Issue: Meta-analysis not completed
**Solution**: Either complete the meta-analysis or manually update status:

```sql
UPDATE meta_analyses
SET status = 'completed'
WHERE id = 'your-id';
```

### Issue: Claude API errors
**Solution**: Check your API key is set:

```bash
echo $ANTHROPIC_API_KEY
```

Should start with `sk-ant-`

---

## 📖 Next Steps

1. **Read full documentation**: `RESEARCH_DIRECTION_README.md`
2. **Explore API endpoints**: http://localhost:8000/docs
3. **Integrate with frontend**: Build UI for Tool 2
4. **Export functionality**: Add PDF/Word export
5. **Deploy to production**: Use Railway or your platform

---

## 🎯 Common Use Cases

### Generate Directions for Existing Meta-Analysis

```bash
# Get your meta-analyses
curl -X GET http://localhost:8000/api/v1/meta-analysis/list \
  -H "Authorization: Bearer $TOKEN"

# Pick one with status="completed"
# Generate directions
curl -X POST http://localhost:8000/api/v1/research-direction/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"meta_analysis_id\": \"YOUR_ID\",
    \"max_proposals\": 3
  }"
```

### View All Your Research Directions

```bash
curl -X GET http://localhost:8000/api/v1/research-direction/history?limit=10 \
  -H "Authorization: Bearer $TOKEN"
```

### Focus on Specific Gaps

```bash
curl -X POST http://localhost:8000/api/v1/research-direction/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"meta_analysis_id\": \"YOUR_ID\",
    \"focus_areas\": [\"methodology\"],
    \"max_proposals\": 3
  }"
```

---

## 💡 Pro Tips

1. **Complete meta-analysis first**: Better input = better output
2. **Use focus_areas**: Get targeted gap analysis
3. **Start with 3 proposals**: Faster generation, easier to review
4. **Review feasibility scores**: High feasibility = more realistic
5. **Check completeness score**: Aim for 0.75+

---

## 🎊 You're Ready!

Tool 2 is now operational. Start generating research directions from your meta-analyses!

**Happy researching! 🔬**
