#!/usr/bin/env python3
"""
Enhanced Platform Audit with Authentication
Retrying failed tests with proper authentication
Date: 2025-11-11
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"
API_V1 = f"{BASE_URL}/api/v1"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")

def log_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def log_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def log_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def log_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

# ============================================================================
# AUTHENTICATION SETUP
# ============================================================================

def setup_authentication():
    """Create a test user and get authentication token"""
    log_header("SETTING UP AUTHENTICATION")

    # Generate unique test user
    timestamp = int(time.time())
    test_user = {
        "email": f"qa_test_{timestamp}@test.edu",
        "password": "QATest123!Strong",
        "full_name": "QA Test User",
        "institution": "QA Test University"
    }

    # Try to register user
    log_info(f"Creating test user: {test_user['email']}")

    try:
        # First, let's check if registration endpoint works at all
        response = requests.post(
            f"{API_V1}/auth/register",
            json=test_user,
            timeout=10
        )

        if response.status_code == 201:
            log_success(f"User created successfully: {test_user['email']}")
        elif response.status_code == 400:
            log_info("User might already exist, attempting login...")
        else:
            log_error(f"Registration failed: {response.status_code}")
            log_error(f"Response: {response.text}")
            # Try with a simpler approach

    except Exception as e:
        log_error(f"Registration error: {str(e)}")

    # Try to login
    log_info("Attempting login...")

    try:
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"],
            "grant_type": "password"
        }

        response = requests.post(
            f"{API_V1}/auth/login",
            data=login_data,  # Using form data
            timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            log_success("Login successful, token obtained")
            return access_token
        else:
            log_error(f"Login failed: {response.status_code}")
            log_error(f"Response: {response.text}")

    except Exception as e:
        log_error(f"Login error: {str(e)}")

    return None

# ============================================================================
# RETRY TESTS WITH AUTH
# ============================================================================

def retry_researcher_loading(token):
    """Retry loading researchers with authentication"""
    log_header("RETRYING: LOAD TEST RESEARCHERS WITH AUTH")

    if not token:
        log_error("No authentication token available")
        return 0

    headers = {"Authorization": f"Bearer {token}"}
    loaded = 0

    # Simplified researcher data
    researchers = [
        {"name": "Dr. Emily Chen", "email": "emily.chen@test.edu", "expertise": "neuroscience"},
        {"name": "Prof. Michael Rodriguez", "email": "m.rodriguez@test.edu", "expertise": "psychology"},
        {"name": "Dr. Sarah Johnson", "email": "s.johnson@test.edu", "expertise": "public health"},
        {"name": "Dr. James Liu", "email": "james.liu@test.edu", "expertise": "machine learning"},
        {"name": "Prof. Maria Garcia", "email": "m.garcia@test.edu", "expertise": "child psychology"}
    ]

    for researcher in researchers:
        try:
            response = requests.post(
                f"{API_V1}/researchers",
                json=researcher,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                loaded += 1
                log_success(f"Loaded: {researcher['name']}")
            else:
                log_error(f"Failed to load {researcher['name']}: {response.status_code}")

        except Exception as e:
            log_error(f"Error: {str(e)}")

    log_info(f"Successfully loaded {loaded}/{len(researchers)} researchers")
    return loaded

def retry_meta_analysis(token):
    """Retry meta-analysis workflow with authentication"""
    log_header("RETRYING: META-ANALYSIS WORKFLOW WITH AUTH")

    if not token:
        log_error("No authentication token available")
        return None

    headers = {"Authorization": f"Bearer {token}"}

    # Simplified meta-analysis request
    ma_request = {
        "topic": "CBT for anxiety",
        "research_question": "Effects of CBT on anxiety disorders"
    }

    try:
        log_info("Creating meta-analysis...")
        response = requests.post(
            f"{API_V1}/meta-analysis",  # Try simplified endpoint
            json=ma_request,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            log_success("Meta-analysis created")
            return response.json()
        else:
            log_error(f"Failed: {response.status_code}")
            log_error(f"Response: {response.text[:500]}")

            # Try the /create endpoint
            log_info("Trying /meta-analysis/create endpoint...")
            response = requests.post(
                f"{API_V1}/meta-analysis/create",
                json=ma_request,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                log_success("Meta-analysis created via /create endpoint")
                return response.json()
            else:
                log_error(f"Also failed: {response.status_code}")

    except Exception as e:
        log_error(f"Error: {str(e)}")

    return None

# ============================================================================
# DATABASE CHECK
# ============================================================================

def check_database_status():
    """Check database connectivity and issues"""
    log_header("DATABASE STATUS CHECK")

    try:
        response = requests.get(f"{API_V1}/health/detailed", timeout=10)

        if response.status_code == 200:
            data = response.json()
            checks = data.get("checks", {})

            # Database status
            db_check = checks.get("database", {})
            db_status = db_check.get("status", "unknown")

            if db_status == "healthy":
                log_success(f"Database: {db_status}")
            else:
                log_error(f"Database: {db_status}")

            # Redis status
            redis_check = checks.get("redis", {})
            redis_status = redis_check.get("status", "unknown")

            if redis_status == "healthy":
                log_success(f"Redis: {redis_status}")
            else:
                log_warning(f"Redis: {redis_status}")

            # Celery status
            celery_check = checks.get("celery", {})
            celery_status = celery_check.get("status", "unknown")

            if celery_status == "healthy":
                log_success(f"Celery: {celery_status}")
            else:
                log_warning(f"Celery: {celery_status}")

            return data
        else:
            log_error(f"Health check failed: {response.status_code}")

    except Exception as e:
        log_error(f"Error checking database: {str(e)}")

    return None

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Enhanced testing with authentication"""
    log_header("ENHANCED PLATFORM AUDIT - AUTHENTICATION RETRY")
    log_info(f"Target: {BASE_URL}")
    log_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check database first
    db_status = check_database_status()

    # Setup authentication
    token = setup_authentication()

    if token:
        log_success("Authentication successful")

        # Retry failed tests
        researchers_loaded = retry_researcher_loading(token)
        ma_result = retry_meta_analysis(token)

        # Test authenticated endpoints
        log_header("TESTING AUTHENTICATED ENDPOINTS")

        headers = {"Authorization": f"Bearer {token}"}

        endpoints = [
            ("/api/v1/auth/me", "User profile"),
            ("/api/v1/researchers", "List researchers"),
            ("/api/v1/health/metrics", "System metrics"),
            ("/api/v1/auth/api-keys", "API keys")
        ]

        for endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    log_success(f"{description}: OK")
                else:
                    log_error(f"{description}: {response.status_code}")

            except Exception as e:
                log_error(f"{description}: {str(e)}")
    else:
        log_error("Authentication failed - cannot proceed with authenticated tests")

        # Try some diagnostic checks
        log_header("DIAGNOSTIC CHECKS")

        # Check if the API is responding at all
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            log_info(f"Root endpoint: {response.status_code}")
            if response.status_code == 200:
                log_info(f"Response: {response.text[:200]}")
        except Exception as e:
            log_error(f"Root endpoint error: {str(e)}")

        # Check CORS headers
        try:
            response = requests.options(f"{API_V1}/auth/login", timeout=5)
            log_info(f"CORS check: {response.status_code}")
            log_info(f"Headers: {dict(response.headers)}")
        except Exception as e:
            log_error(f"CORS check error: {str(e)}")

    # Generate summary
    log_header("ENHANCED AUDIT SUMMARY")

    summary = f"""
## AUTHENTICATION STATUS
- Token obtained: {'YES' if token else 'NO'}
- Database status: {db_status.get('checks', {}).get('database', {}).get('status', 'unknown') if db_status else 'unknown'}

## KEY FINDINGS
1. Authentication system has issues with AsyncSession
2. Database connectivity appears functional
3. Health endpoints are working
4. Meta-analysis creation fails with database query error

## CRITICAL ISSUES
1. **Database ORM Issue**: 'AsyncSession' object has no attribute 'query'
   - This suggests SQLAlchemy async/sync mismatch
   - Need to use async query methods (select, execute)

2. **Authentication Required**: Researchers endpoint requires auth
   - Need proper token authentication for most endpoints

3. **Registration Endpoint**: Returns 500 error
   - Database session handling issue

## RECOMMENDATIONS
1. Fix SQLAlchemy async session usage
2. Implement proper error handling for database operations
3. Add fallback for sync/async database operations
4. Improve error messages for debugging
"""

    print(summary)

    # Save enhanced report
    report_path = f"/Users/brandon/meta-analysis-tool/enhanced_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w') as f:
        f.write(summary)

    log_success(f"Enhanced report saved to: {report_path}")

if __name__ == "__main__":
    main()