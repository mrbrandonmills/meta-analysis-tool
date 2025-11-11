#!/usr/bin/env python3
"""
Demo script to test progress tracking system
This simulates a long-running task with progress updates
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

import time
import asyncio
from app.workers.tasks.progress_helper import create_meta_analysis_reporter

def simulate_meta_analysis():
    """
    Simulate a meta-analysis task with progress updates
    """
    print("=" * 60)
    print("Progress Tracking Demo - Meta-Analysis Simulation")
    print("=" * 60)
    print()

    # Create progress reporter
    task_id = "demo-test-001"
    reporter = create_meta_analysis_reporter(task_id, num_studies=150)

    print(f"Task ID: {task_id}")
    print(f"Task Type: meta-analysis")
    print(f"Estimated Time: {reporter.estimated_total_time} seconds")
    print(f"Total Steps: {reporter.total_steps}")
    print()
    print("Starting task...")
    print()

    # Start the task
    reporter.start()
    time.sleep(1)

    # Simulate each step
    steps = [
        ("Literature Search", 5, "Searching PubMed, Web of Science, and Scopus..."),
        ("Study Screening", 8, "Applying inclusion/exclusion criteria to 150 studies..."),
        ("Quality Assessment", 6, "Evaluating study quality and risk of bias..."),
        ("Data Extraction", 7, "Extracting outcome data from included studies..."),
        ("Statistical Analysis", 10, "Calculating effect sizes and heterogeneity..."),
        ("Report Generation", 4, "Generating APA-formatted systematic review report...")
    ]

    for i, (step_name, duration, message) in enumerate(steps):
        print(f"Step {i+1}/{len(steps)}: {step_name}")
        print(f"  {message}")

        # Update progress
        reporter.update_step(i, message)

        # Simulate work
        for j in range(duration):
            time.sleep(1)
            dots = "." * ((j + 1) % 4)
            print(f"  Working{dots:<3}", end="\r")

        print(f"  ✓ {step_name} complete!")
        print()

    # Mark as complete
    reporter.complete()

    print()
    print("=" * 60)
    print("Task Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Open http://localhost:3000/tools/meta-analysis/new")
    print(f"2. Check Redis: redis-cli GET 'progress:meta-analysis:{task_id}'")
    print("3. API endpoint: GET /api/v1/tasks/{task_id}/progress?task_type=meta-analysis")
    print()


def test_progress_api():
    """
    Test the progress API directly
    """
    import redis
    import json

    print("=" * 60)
    print("Testing Progress API")
    print("=" * 60)
    print()

    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✓ Redis connection successful")
        print()

        # Create test progress data
        task_id = "api-test-001"
        progress_data = {
            "progress": 67,
            "status": "running",
            "estimated_time_remaining": 180,
            "current_step": "Statistical Analysis in progress",
            "steps_completed": [
                "Literature Search",
                "Study Screening",
                "Quality Assessment"
            ],
            "steps_remaining": [
                "Data Extraction",
                "Statistical Analysis",
                "Report Generation"
            ],
            "started_at": "2025-11-10T18:00:00Z",
            "estimated_completion": "2025-11-10T18:05:00Z"
        }

        # Store in Redis
        key = f"progress:meta-analysis:{task_id}"
        r.setex(key, 3600, json.dumps(progress_data))
        print(f"✓ Progress data stored in Redis")
        print(f"  Key: {key}")
        print(f"  TTL: 3600 seconds (1 hour)")
        print()

        # Retrieve and display
        stored = r.get(key)
        if stored:
            data = json.loads(stored)
            print("✓ Progress data retrieved:")
            print(f"  Progress: {data['progress']}%")
            print(f"  Status: {data['status']}")
            print(f"  Current Step: {data['current_step']}")
            print(f"  Time Remaining: {data['estimated_time_remaining']}s")
            print(f"  Steps Completed: {len(data['steps_completed'])}")
            print(f"  Steps Remaining: {len(data['steps_remaining'])}")
        else:
            print("✗ Failed to retrieve progress data")

        print()
        print("=" * 60)
        print("API Test Complete!")
        print("=" * 60)
        print()
        print("Test the API endpoint:")
        print(f"  curl 'http://localhost:8000/api/v1/tasks/{task_id}/progress?task_type=meta-analysis'")
        print()

    except redis.ConnectionError:
        print("✗ Redis connection failed")
        print("  Make sure Redis is running:")
        print("    macOS: brew services start redis")
        print("    Linux: sudo systemctl start redis")
        print()
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    return True


def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test progress tracking system")
    parser.add_argument(
        '--mode',
        choices=['simulate', 'api', 'both'],
        default='both',
        help='Test mode (default: both)'
    )

    args = parser.parse_args()

    if args.mode in ['api', 'both']:
        success = test_progress_api()
        if not success:
            print("API test failed. Fix errors before continuing.")
            return

        if args.mode == 'api':
            return

        print()
        input("Press Enter to continue with simulation...")
        print()

    if args.mode in ['simulate', 'both']:
        simulate_meta_analysis()


if __name__ == '__main__':
    main()
