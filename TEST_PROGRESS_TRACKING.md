# Progress Tracking & Notifications - Test Guide

This document provides comprehensive testing instructions for the real-time progress tracking and notification system.

## Features Implemented

### 1. Frontend Components
- **Progress Tracking Hook** (`/frontend/src/hooks/useProgressTracking.ts`)
  - Real-time polling (2-second intervals)
  - Time estimation and countdown
  - Auto-pause when tab hidden
  - Completion callbacks

- **Progress Tracker Component** (`/frontend/src/components/workflow/ProgressTracker.tsx`)
  - Beautiful glassmorphism UI
  - Animated progress bar with shimmer effect
  - Step-by-step progress display
  - Time remaining countdown
  - Completion animations

- **Notification System** (`/frontend/src/lib/notifications.ts`)
  - Browser notifications (Desktop/Mobile)
  - Sound alerts (success, error, info)
  - Vibration (mobile devices)
  - Permission management

### 2. Backend API
- **Progress Endpoint** (`/backend/app/api/v1/progress.py`)
  - `GET /api/v1/tasks/{task_id}/progress` - Get progress
  - `DELETE /api/v1/tasks/{task_id}/progress` - Clear progress
  - Redis-based progress storage
  - Time estimation algorithms

- **Progress Helper** (`/backend/app/workers/tasks/progress_helper.py`)
  - `ProgressReporter` class for task tracking
  - Convenience functions for each task type
  - Auto-calculation of time estimates

### 3. Integration
- **Meta-Analysis Page** (`/frontend/src/pages/tools/meta-analysis/new.tsx`)
  - Integrated ProgressTracker component
  - Notification triggers on completion
  - Bell icon showing notification status

## Testing Instructions

### Prerequisites
```bash
# 1. Install dependencies
cd frontend && npm install
cd ../backend && pip install redis

# 2. Start Redis (required for progress tracking)
# macOS:
brew install redis
brew services start redis

# Linux:
sudo apt-get install redis-server
sudo systemctl start redis

# Windows:
# Download from https://github.com/microsoftarchive/redis/releases
# Run redis-server.exe

# 3. Verify Redis is running
redis-cli ping
# Should return: PONG
```

### Test 1: Basic Progress Tracking

**Objective:** Test that progress updates work correctly

**Steps:**
1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to http://localhost:3000/tools/meta-analysis/new

4. Fill out the meta-analysis form:
   - Research Question: "Test progress tracking"
   - Topic: "test"
   - Click "Start Analysis"

5. Observe the ProgressTracker component:
   - Progress bar should animate smoothly
   - Time remaining should countdown
   - Current step should update
   - Steps should transition from pending → running → completed

**Expected Results:**
- Progress bar animates from 0% to 100%
- Time estimates are displayed and update
- Step transitions are smooth
- Glassmorphism effects render correctly

### Test 2: Notification System

**Objective:** Test browser notifications, sound, and vibration

**Steps:**
1. Open browser console (F12)
2. Navigate to meta-analysis page
3. Look for notification permission prompt
4. Click "Allow" when prompted
5. Submit a meta-analysis
6. Switch to a different browser tab or application
7. Wait for completion

**Expected Results:**
- Permission prompt appears on first visit
- Bell icon shows "Notifications enabled" when permitted
- Browser notification appears when task completes
- Notification sound plays (pleasant chime)
- Mobile device vibrates (if testing on mobile)
- Clicking notification focuses the window

**Testing Different Scenarios:**

A. **Success Notification:**
   - Complete a task successfully
   - Sound: Success chime
   - Vibration: [200ms, 100ms, 200ms]
   - Icon: Green checkmark

B. **Error Notification:**
   - Trigger an error (invalid input)
   - Sound: Error tone
   - Vibration: [100ms, 50ms, 100ms, 50ms, 100ms]
   - Icon: Red alert

### Test 3: Progress API Endpoints

**Objective:** Test backend API directly

**Using curl:**
```bash
# 1. Create a test progress entry
redis-cli SET "progress:meta-analysis:test-123" '{"progress": 50, "status": "running", "current_step": "Processing", "estimated_time_remaining": 60}'

# 2. Get progress
curl -X GET "http://localhost:8000/api/v1/tasks/test-123/progress?task_type=meta-analysis"

# Expected response:
{
  "progress": 50,
  "status": "running",
  "estimated_time_remaining": 60,
  "current_step": "Processing",
  "steps_completed": [],
  "steps_remaining": [],
  "started_at": "2025-11-10T...",
  "estimated_completion": "2025-11-10T..."
}

# 3. Clear progress
curl -X DELETE "http://localhost:8000/api/v1/tasks/test-123/progress?task_type=meta-analysis"
```

**Using Python:**
```python
import requests
import time

# Test progress tracking
task_id = "test-456"
base_url = "http://localhost:8000/api/v1"

# Simulate progress updates
for i in range(0, 101, 10):
    progress = {
        "progress": i,
        "status": "running" if i < 100 else "completed",
        "current_step": f"Step {i//10 + 1}",
        "estimated_time_remaining": 100 - i
    }

    # In real usage, this would be called from worker tasks
    # For testing, directly call the API
    print(f"Progress: {i}%")
    time.sleep(2)

# Check final status
response = requests.get(f"{base_url}/tasks/{task_id}/progress?task_type=meta-analysis")
print(response.json())
```

### Test 4: Time Estimation Accuracy

**Objective:** Verify time estimates are reasonable

**Test Data:**

```python
# Test time estimation function
from app.api.v1.progress import estimate_task_time

# Meta-analysis (100 studies, 6 agents)
time_ma = estimate_task_time('meta-analysis', {
    'num_studies': 100,
    'num_agents': 6
})
print(f"Meta-analysis: {time_ma}s (~{time_ma/60:.1f} minutes)")
# Expected: ~170 seconds (2.8 minutes)

# Peer review (20 pages)
time_pr = estimate_task_time('peer-review', {
    'num_pages': 20
})
print(f"Peer review: {time_pr}s (~{time_pr/60:.1f} minutes)")
# Expected: ~85 seconds (1.4 minutes)

# Reviewer matcher (500 experts)
time_rm = estimate_task_time('reviewer-matcher', {
    'pool_size': 500
})
print(f"Reviewer matcher: {time_rm}s (~{time_rm/60:.1f} minutes)")
# Expected: ~80 seconds (1.3 minutes)
```

**Validation:**
- Estimates should be within 20% of actual completion time
- Larger inputs should result in longer estimates
- Estimates should update dynamically based on actual progress

### Test 5: Mobile Device Testing

**Objective:** Test notifications and vibration on mobile

**Steps:**
1. Deploy to Vercel or access via ngrok:
   ```bash
   npm run dev
   ngrok http 3000
   ```

2. Open the ngrok URL on your mobile device

3. Grant notification permissions when prompted

4. Submit a meta-analysis task

5. Lock your device or switch to another app

6. Wait for completion

**Expected Results:**
- Notification appears on lock screen
- Device vibrates with pattern
- Sound plays (if not on silent)
- Tapping notification opens the app

### Test 6: Walk Away Scenario

**Objective:** Verify users can walk away and return

**Steps:**
1. Start a long-running meta-analysis (many studies)
2. Minimize the browser window
3. Do other work for several minutes
4. Listen for notification sound
5. Return to browser when notified

**Expected Results:**
- Polling continues while minimized
- Notification triggers when complete
- Progress is current when returned
- No errors or timeouts

### Test 7: Error Handling

**Objective:** Test error scenarios

**Scenarios to Test:**

A. **Redis Unavailable:**
   ```bash
   # Stop Redis
   brew services stop redis  # macOS
   sudo systemctl stop redis  # Linux

   # Try to get progress
   # Should return graceful error, not crash
   ```

B. **Invalid Task ID:**
   ```bash
   curl "http://localhost:8000/api/v1/tasks/invalid-id/progress?task_type=meta-analysis"
   # Should return pending status, not 404
   ```

C. **Network Disconnection:**
   - Start a task
   - Disconnect WiFi
   - Reconnect after 30 seconds
   - Progress should resume polling

**Expected Results:**
- Graceful degradation (no crashes)
- Clear error messages
- Automatic recovery when possible

### Test 8: Performance Testing

**Objective:** Verify system handles load

**Test Script:**
```python
import asyncio
import aiohttp
import time

async def poll_progress(session, task_id):
    url = f"http://localhost:8000/api/v1/tasks/{task_id}/progress?task_type=meta-analysis"
    async with session.get(url) as response:
        return await response.json()

async def test_concurrent_polling():
    async with aiohttp.ClientSession() as session:
        tasks = [
            poll_progress(session, f"task-{i}")
            for i in range(100)
        ]

        start = time.time()
        results = await asyncio.gather(*tasks)
        duration = time.time() - start

        print(f"Polled 100 tasks in {duration:.2f}s")
        print(f"Average: {duration/100*1000:.1f}ms per request")

asyncio.run(test_concurrent_polling())
```

**Expected Performance:**
- 100 concurrent requests < 2 seconds
- Average response time < 50ms
- No memory leaks over time
- Redis memory usage stays reasonable

## Troubleshooting

### Notifications Not Showing

**Problem:** Browser notifications don't appear

**Solutions:**
1. Check browser settings:
   - Chrome: Settings → Privacy → Site Settings → Notifications
   - Firefox: Preferences → Privacy & Security → Permissions → Notifications
   - Safari: Preferences → Websites → Notifications

2. Check notification permission:
   ```javascript
   console.log('Permission:', Notification.permission)
   // Should be: "granted"
   ```

3. Try requesting permission manually:
   ```javascript
   Notification.requestPermission()
   ```

### Progress Not Updating

**Problem:** Progress bar doesn't move

**Solutions:**
1. Verify Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check browser console for errors

3. Verify API endpoint is accessible:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

4. Check network tab in DevTools:
   - Look for 2-second polling requests
   - Verify responses contain progress data

### Sound Not Playing

**Problem:** Notification sound doesn't play

**Solutions:**
1. Check browser console for audio errors

2. Verify browser allows audio:
   - Some browsers block audio without user interaction
   - Click anywhere on page first

3. Check system volume and mute status

4. Try playing sound manually:
   ```javascript
   const audio = new Audio('data:audio/wav;base64,...')
   audio.play()
   ```

### Vibration Not Working

**Problem:** Device doesn't vibrate

**Solutions:**
1. Verify device supports vibration:
   ```javascript
   console.log('Vibration API:', 'vibrate' in navigator)
   ```

2. Check device is not on silent/vibrate-off mode

3. Test vibration manually:
   ```javascript
   navigator.vibrate(200)
   ```

4. Note: iOS Safari doesn't support vibration API

## Success Criteria

The progress tracking system is working correctly when:

- [ ] Progress bar animates smoothly from 0-100%
- [ ] Time estimates display and countdown
- [ ] Steps transition correctly (pending → running → completed)
- [ ] Browser notifications appear on completion
- [ ] Notification sound plays
- [ ] Mobile devices vibrate (when supported)
- [ ] Users can walk away and return
- [ ] Polling pauses when tab hidden
- [ ] System handles errors gracefully
- [ ] API responds within acceptable time (<100ms)
- [ ] Redis stores progress correctly
- [ ] Completion triggers all notification methods

## Known Limitations

1. **Browser Support:**
   - Notifications require HTTPS in production
   - Safari on iOS doesn't support vibration
   - Some browsers block audio autoplay

2. **Polling vs WebSockets:**
   - Current implementation uses polling
   - WebSocket upgrade recommended for production
   - Reduces server load and improves real-time feel

3. **Time Estimates:**
   - Based on averages, may not be perfectly accurate
   - Improve over time with historical data
   - Dynamic adjustment during execution

4. **Redis Dependency:**
   - Requires Redis for progress tracking
   - Falls back gracefully if unavailable
   - Consider clustered Redis for production

## Future Enhancements

1. **WebSocket Support:**
   - Push updates instead of polling
   - Reduces latency and server load
   - More scalable for many users

2. **Historical Analytics:**
   - Track actual completion times
   - Improve time estimates over time
   - Show accuracy metrics

3. **Customizable Notifications:**
   - User-configurable sounds
   - Custom notification frequency
   - Email notifications for long tasks

4. **Progress Milestones:**
   - Notify at 25%, 50%, 75% completion
   - Configurable milestone points
   - Different sounds for milestones

5. **Multi-Task Dashboard:**
   - View all running tasks
   - Pause/resume tasks
   - Priority management

## Documentation

- **Hook Documentation:** `/frontend/src/hooks/useProgressTracking.ts`
- **Component Documentation:** `/frontend/src/components/workflow/ProgressTracker.tsx`
- **API Documentation:** `/backend/app/api/v1/progress.py`
- **Notification Documentation:** `/frontend/src/lib/notifications.ts`

## Support

For issues or questions:
1. Check this test guide first
2. Review component documentation
3. Check browser console for errors
4. Verify Redis is running
5. Test API endpoints directly

## Conclusion

This comprehensive test guide ensures the progress tracking and notification system works correctly across all scenarios. Follow each test systematically to verify functionality before production deployment.
