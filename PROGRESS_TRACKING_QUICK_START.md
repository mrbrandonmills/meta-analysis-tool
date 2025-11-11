# Progress Tracking - Quick Start Guide

Get the real-time progress tracking and notifications system up and running in 5 minutes!

## Prerequisites

1. **Redis** (required for progress storage)
2. **Node.js** and **Python** installed
3. Working meta-analysis platform

## Step 1: Install Redis (2 minutes)

### macOS
```bash
brew install redis
brew services start redis
redis-cli ping  # Should return PONG
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
redis-cli ping  # Should return PONG
```

### Windows
1. Download from https://github.com/microsoftarchive/redis/releases
2. Run `redis-server.exe`
3. Test with `redis-cli.exe ping`

## Step 2: Install Dependencies (1 minute)

```bash
# Backend
cd backend
pip install redis

# Frontend (already installed if you have the project)
cd frontend
npm install  # If not already done
```

## Step 3: Test the System (2 minutes)

### Test 1: Verify Redis Connection
```bash
python test_progress_demo.py --mode api
```

Expected output:
```
✓ Redis connection successful
✓ Progress data stored in Redis
✓ Progress data retrieved
API Test Complete!
```

### Test 2: Run Full Simulation
```bash
python test_progress_demo.py --mode simulate
```

Watch the simulated progress updates!

## Step 4: Start the Application

### Terminal 1: Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

## Step 5: Try It Out!

1. Open http://localhost:3000/tools/meta-analysis/new
2. Fill out the form:
   - Research Question: "Test progress tracking"
   - Topic: "test"
3. Click "Start Analysis"
4. Watch the beautiful progress tracker!
5. When prompted, allow notifications
6. Switch to another tab or app
7. Wait for the notification sound and alert!

## What to Expect

### Visual Progress
```
┌────────────────────────────────────────────┐
│  🔬 Running Meta-Analysis                  │
├────────────────────────────────────────────┤
│  ⏱️  Estimated time: 2 minutes 30 seconds │
│  📊 Progress: 67% complete                 │
│                                            │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░                │
│                                            │
│  Current: Screening 150 studies...        │
│                                            │
│  ✅ Literature Search complete             │
│  ✅ Study Screening complete               │
│  🔄 Quality Assessment in progress...     │
│  ⏳ Data Extraction pending               │
│  ⏳ Statistical Analysis pending          │
│  ⏳ Report Generation pending             │
└────────────────────────────────────────────┘
```

### Notification
When complete:
- 🔔 Browser notification appears
- 🔊 Success sound plays
- 📱 Device vibrates (mobile)
- ✨ Completion animation shows

## Troubleshooting

### Redis not connecting?
```bash
# Check if Redis is running
redis-cli ping

# If not, start it
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Notifications not showing?
1. Click the bell icon to request permission
2. Check browser settings → Notifications
3. Allow notifications for localhost

### Progress not updating?
1. Open browser DevTools (F12)
2. Check Network tab for polling requests
3. Look for errors in Console
4. Verify backend is running

## API Endpoints

Test the API directly:

```bash
# Get progress
curl "http://localhost:8000/api/v1/tasks/demo-test-001/progress?task_type=meta-analysis"

# Health check
curl "http://localhost:8000/api/v1/health"
```

## Next Steps

1. **Read Full Documentation:**
   - `PROGRESS_TRACKING_IMPLEMENTATION.md` - Complete docs
   - `TEST_PROGRESS_TRACKING.md` - Comprehensive tests

2. **Customize:**
   - Add custom icons in `/frontend/public/`
   - Adjust polling interval in hook
   - Customize notification sounds

3. **Deploy:**
   - Ensure Redis is available in production
   - Set up Redis cluster for scale
   - Configure HTTPS for notifications

## Quick Reference

### Files Created
```
Frontend:
  /frontend/src/hooks/useProgressTracking.ts
  /frontend/src/components/workflow/ProgressTracker.tsx
  /frontend/src/lib/notifications.ts
  /frontend/src/pages/tools/meta-analysis/new.tsx (modified)

Backend:
  /backend/app/api/v1/progress.py
  /backend/app/workers/tasks/progress_helper.py
  /backend/app/main.py (modified)

Documentation:
  /PROGRESS_TRACKING_IMPLEMENTATION.md
  /TEST_PROGRESS_TRACKING.md
  /test_progress_demo.py
```

### Key Commands
```bash
# Test Redis
redis-cli ping

# Run demo
python test_progress_demo.py

# Start backend
cd backend && python -m uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev

# Check API
curl localhost:8000/api/v1/health
```

## Success Checklist

- [ ] Redis installed and running
- [ ] Demo test passes (`python test_progress_demo.py`)
- [ ] Backend starts without errors
- [ ] Frontend loads successfully
- [ ] Progress bar animates smoothly
- [ ] Time estimates display
- [ ] Notifications work (after permission granted)
- [ ] Sound plays on completion
- [ ] Can walk away and get notified

## Support

If you encounter issues:

1. **Check Redis:** `redis-cli ping`
2. **Check Logs:** Backend console and browser DevTools
3. **Run Demo:** `python test_progress_demo.py`
4. **Read Docs:** `TEST_PROGRESS_TRACKING.md`

## Resources

- **Full Documentation:** `PROGRESS_TRACKING_IMPLEMENTATION.md`
- **Test Guide:** `TEST_PROGRESS_TRACKING.md`
- **Demo Script:** `test_progress_demo.py`
- **API Docs:** http://localhost:8000/docs (when running)

---

**That's it!** You now have real-time progress tracking with notifications. Users can walk away and get notified when their research is complete. 🎉
