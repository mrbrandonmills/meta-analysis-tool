#!/usr/bin/env python3
"""
Comprehensive QA Audit for Meta-Analysis Research Platform
Author: QA Engineer Agent
Date: 2025-11-05
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://meta-analysis-tool-production.up.railway.app"
TEST_RESULTS = []
BUG_REPORTS = []

class TestResult:
    def __init__(self, category: str, test_name: str, status: str,
                 details: Dict[str, Any] = None, severity: str = None):
        self.category = category
        self.test_name = test_name
        self.status = status  # PASS, FAIL, ERROR
        self.details = details or {}
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "category": self.category,
            "test_name": self.test_name,
            "status": self.status,
            "details": self.details,
            "severity": self.severity,
            "timestamp": self.timestamp
        }

def log_test(result: TestResult):
    """Log test result and add to global list."""
    TEST_RESULTS.append(result)
    status_symbol = "✓" if result.status == "PASS" else "✗"
    print(f"{status_symbol} [{result.category}] {result.test_name}: {result.status}")
    if result.details:
        print(f"   Details: {json.dumps(result.details, indent=2)}")

def log_bug(category: str, title: str, description: str, severity: str,
            reproduction_steps: List[str], expected: str, actual: str):
    """Log a bug report."""
    bug = {
        "id": f"BUG-{len(BUG_REPORTS) + 1:03d}",
        "category": category,
        "title": title,
        "description": description,
        "severity": severity,
        "reproduction_steps": reproduction_steps,
        "expected_result": expected,
        "actual_result": actual,
        "timestamp": datetime.now().isoformat()
    }
    BUG_REPORTS.append(bug)
    print(f"\n🐛 BUG FOUND: {bug['id']} - {title} (Severity: {severity})")

# ============================================================================
# TEST SUITE 1: HEALTH & SYSTEM STATUS
# ============================================================================

def test_health_endpoints():
    """Test all health check endpoints."""
    print("\n" + "="*80)
    print("TEST SUITE 1: HEALTH & SYSTEM STATUS")
    print("="*80)

    # Test 1.1: Basic health check
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test(TestResult("Health", "Basic Health Check", "PASS",
                              {"status": data.get("status"), "response_time": response.elapsed.total_seconds()}))
        else:
            log_test(TestResult("Health", "Basic Health Check", "FAIL",
                              {"status_code": response.status_code}, "HIGH"))
            log_bug("Health", "Health endpoint returns non-200",
                   f"Health endpoint returned {response.status_code}",
                   "HIGH", [f"curl {BASE_URL}/api/v1/health"],
                   "200 OK with health status", f"{response.status_code}: {response.text}")
    except Exception as e:
        log_test(TestResult("Health", "Basic Health Check", "ERROR", {"error": str(e)}, "CRITICAL"))

    # Test 1.2: Detailed health check
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/detailed", timeout=10)
        if response.status_code == 200:
            data = response.json()
            checks = data.get("checks", {})

            # Check database status
            db_status = checks.get("database", {}).get("status")
            if db_status == "healthy":
                log_test(TestResult("Health", "Database Health", "PASS"))
            else:
                log_test(TestResult("Health", "Database Health", "FAIL",
                                  {"db_status": db_status}, "CRITICAL"))
                log_bug("Database", "Database unhealthy",
                       "Database health check shows unhealthy status",
                       "CRITICAL", [f"curl {BASE_URL}/api/v1/health/detailed"],
                       "Database status: healthy", f"Database status: {db_status}")

            # Check Redis status
            redis_status = checks.get("redis", {}).get("status")
            if redis_status == "healthy":
                log_test(TestResult("Health", "Redis Health", "PASS"))
            else:
                log_test(TestResult("Health", "Redis Health", "FAIL",
                                  {"redis_status": redis_status}, "HIGH"))
                log_bug("Infrastructure", "Redis unhealthy",
                       "Redis health check shows unhealthy status",
                       "HIGH", [f"curl {BASE_URL}/api/v1/health/detailed"],
                       "Redis status: healthy", f"Redis status: {redis_status}")

            # Check Celery status (warning only if degraded)
            celery_status = checks.get("celery", {}).get("status")
            if celery_status in ["healthy", "degraded"]:
                log_test(TestResult("Health", "Celery Workers", "PASS" if celery_status == "healthy" else "WARN",
                                  {"celery_status": celery_status, "message": checks.get("celery", {}).get("message")}))
                if celery_status == "degraded":
                    print("   ⚠️  WARNING: Celery workers degraded - background jobs may be affected")
            else:
                log_test(TestResult("Health", "Celery Workers", "FAIL",
                                  {"celery_status": celery_status}, "MEDIUM"))
        else:
            log_test(TestResult("Health", "Detailed Health Check", "FAIL",
                              {"status_code": response.status_code}, "HIGH"))
    except Exception as e:
        log_test(TestResult("Health", "Detailed Health Check", "ERROR", {"error": str(e)}, "HIGH"))

    # Test 1.3: Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("name") == "Meta-Analysis Research Platform":
                log_test(TestResult("Health", "Root Endpoint", "PASS",
                                  {"version": data.get("version"), "status": data.get("status")}))
            else:
                log_test(TestResult("Health", "Root Endpoint", "FAIL",
                                  {"unexpected_response": data}, "MEDIUM"))
        else:
            log_test(TestResult("Health", "Root Endpoint", "FAIL",
                              {"status_code": response.status_code}, "HIGH"))
    except Exception as e:
        log_test(TestResult("Health", "Root Endpoint", "ERROR", {"error": str(e)}, "HIGH"))

    # Test 1.4: Swagger docs accessibility
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        if response.status_code == 200 and "swagger" in response.text.lower():
            log_test(TestResult("Documentation", "Swagger Docs", "PASS"))
        else:
            log_test(TestResult("Documentation", "Swagger Docs", "FAIL",
                              {"status_code": response.status_code}, "MEDIUM"))
            log_bug("Documentation", "Swagger docs not accessible",
                   "Swagger documentation endpoint not returning expected content",
                   "MEDIUM", [f"curl {BASE_URL}/docs"],
                   "Swagger UI HTML", f"Status {response.status_code}")
    except Exception as e:
        log_test(TestResult("Documentation", "Swagger Docs", "ERROR", {"error": str(e)}, "MEDIUM"))

# ============================================================================
# TEST SUITE 2: AUTHENTICATION & AUTHORIZATION
# ============================================================================

def test_authentication():
    """Test all authentication endpoints."""
    print("\n" + "="*80)
    print("TEST SUITE 2: AUTHENTICATION & AUTHORIZATION")
    print("="*80)

    # Generate unique test user
    timestamp = int(time.time())
    test_user = {
        "email": f"qa_test_{timestamp}@example.com",
        "password": "TestPass123!",
        "full_name": "QA Test User",
        "institution": "Test University"
    }

    # Test 2.1: User registration
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=test_user,
            timeout=10
        )

        if response.status_code == 201:
            user_data = response.json()
            if user_data.get("email") == test_user["email"]:
                log_test(TestResult("Auth", "User Registration", "PASS",
                                  {"user_id": user_data.get("id"), "email": user_data.get("email")}))
                test_user["id"] = user_data.get("id")
            else:
                log_test(TestResult("Auth", "User Registration", "FAIL",
                                  {"unexpected_data": user_data}, "HIGH"))
        else:
            log_test(TestResult("Auth", "User Registration", "FAIL",
                              {"status_code": response.status_code, "response": response.text}, "CRITICAL"))
            log_bug("Authentication", "User registration fails",
                   f"Registration endpoint returned {response.status_code}",
                   "CRITICAL",
                   [f"POST {BASE_URL}/api/v1/auth/register",
                    f"Body: {json.dumps(test_user)}"],
                   "201 Created with user data",
                   f"{response.status_code}: {response.text}")
            return  # Can't continue without registration
    except Exception as e:
        log_test(TestResult("Auth", "User Registration", "ERROR", {"error": str(e)}, "CRITICAL"))
        return

    # Test 2.2: Duplicate registration (should fail)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=test_user,
            timeout=10
        )

        if response.status_code == 400:
            log_test(TestResult("Auth", "Duplicate Registration Prevention", "PASS"))
        else:
            log_test(TestResult("Auth", "Duplicate Registration Prevention", "FAIL",
                              {"status_code": response.status_code}, "HIGH"))
            log_bug("Authentication", "Duplicate registration not prevented",
                   "System allows duplicate email registration",
                   "HIGH",
                   [f"Register user twice with same email"],
                   "400 Bad Request with 'Email already registered'",
                   f"{response.status_code}: {response.text}")
    except Exception as e:
        log_test(TestResult("Auth", "Duplicate Registration Prevention", "ERROR", {"error": str(e)}, "MEDIUM"))

    # Test 2.3: User login
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={
                "username": test_user["email"],
                "password": test_user["password"]
            },
            timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data and "refresh_token" in token_data:
                log_test(TestResult("Auth", "User Login", "PASS",
                                  {"token_type": token_data.get("token_type")}))
                test_user["access_token"] = token_data["access_token"]
                test_user["refresh_token"] = token_data["refresh_token"]
            else:
                log_test(TestResult("Auth", "User Login", "FAIL",
                                  {"missing_tokens": token_data}, "CRITICAL"))
                log_bug("Authentication", "Login missing tokens",
                       "Login successful but tokens not returned",
                       "CRITICAL",
                       [f"POST {BASE_URL}/api/v1/auth/login with valid credentials"],
                       "access_token and refresh_token",
                       f"Response: {token_data}")
        else:
            log_test(TestResult("Auth", "User Login", "FAIL",
                              {"status_code": response.status_code, "response": response.text}, "CRITICAL"))
            log_bug("Authentication", "Login fails with valid credentials",
                   f"Login endpoint returned {response.status_code}",
                   "CRITICAL",
                   [f"POST {BASE_URL}/api/v1/auth/login",
                    f"username={test_user['email']}, password={test_user['password']}"],
                   "200 OK with tokens",
                   f"{response.status_code}: {response.text}")
            return
    except Exception as e:
        log_test(TestResult("Auth", "User Login", "ERROR", {"error": str(e)}, "CRITICAL"))
        return

    # Test 2.4: Invalid login credentials
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={
                "username": test_user["email"],
                "password": "WrongPassword123!"
            },
            timeout=10
        )

        if response.status_code == 401:
            log_test(TestResult("Auth", "Invalid Login Prevention", "PASS"))
        else:
            log_test(TestResult("Auth", "Invalid Login Prevention", "FAIL",
                              {"status_code": response.status_code}, "CRITICAL"))
            log_bug("Security", "Invalid credentials not rejected",
                   "System accepts incorrect password",
                   "CRITICAL",
                   [f"POST {BASE_URL}/api/v1/auth/login with wrong password"],
                   "401 Unauthorized",
                   f"{response.status_code}: {response.text}")
    except Exception as e:
        log_test(TestResult("Auth", "Invalid Login Prevention", "ERROR", {"error": str(e)}, "MEDIUM"))

    # Test 2.5: Get current user (protected endpoint)
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
            timeout=10
        )

        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("email") == test_user["email"]:
                log_test(TestResult("Auth", "Get Current User", "PASS",
                                  {"user_id": user_data.get("id")}))
            else:
                log_test(TestResult("Auth", "Get Current User", "FAIL",
                                  {"unexpected_user": user_data}, "HIGH"))
        else:
            log_test(TestResult("Auth", "Get Current User", "FAIL",
                              {"status_code": response.status_code}, "HIGH"))
            log_bug("Authentication", "Cannot retrieve current user",
                   f"/auth/me endpoint returned {response.status_code}",
                   "HIGH",
                   [f"GET {BASE_URL}/api/v1/auth/me with valid token"],
                   "200 OK with user data",
                   f"{response.status_code}: {response.text}")
    except Exception as e:
        log_test(TestResult("Auth", "Get Current User", "ERROR", {"error": str(e)}, "HIGH"))

    # Test 2.6: Protected endpoint without token
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            timeout=10
        )

        if response.status_code == 401:
            log_test(TestResult("Security", "Auth Required for Protected Endpoints", "PASS"))
        else:
            log_test(TestResult("Security", "Auth Required for Protected Endpoints", "FAIL",
                              {"status_code": response.status_code}, "CRITICAL"))
            log_bug("Security", "Protected endpoint accessible without auth",
                   "Protected endpoint allows access without authentication token",
                   "CRITICAL",
                   [f"GET {BASE_URL}/api/v1/auth/me without Authorization header"],
                   "401 Unauthorized",
                   f"{response.status_code}: Allowed access without token!")
    except Exception as e:
        log_test(TestResult("Security", "Auth Required for Protected Endpoints", "ERROR",
                          {"error": str(e)}, "MEDIUM"))

    # Test 2.7: Token refresh
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/refresh",
            json={"refresh_token": test_user["refresh_token"]},
            timeout=10
        )

        if response.status_code == 200:
            new_tokens = response.json()
            if "access_token" in new_tokens:
                log_test(TestResult("Auth", "Token Refresh", "PASS"))
            else:
                log_test(TestResult("Auth", "Token Refresh", "FAIL",
                                  {"missing_token": new_tokens}, "HIGH"))
        else:
            log_test(TestResult("Auth", "Token Refresh", "FAIL",
                              {"status_code": response.status_code}, "HIGH"))
            log_bug("Authentication", "Token refresh fails",
                   f"Token refresh endpoint returned {response.status_code}",
                   "HIGH",
                   [f"POST {BASE_URL}/api/v1/auth/refresh with valid refresh_token"],
                   "200 OK with new access token",
                   f"{response.status_code}: {response.text}")
    except Exception as e:
        log_test(TestResult("Auth", "Token Refresh", "ERROR", {"error": str(e)}, "HIGH"))

    # Test 2.8: API key creation
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/api-keys",
            json={
                "name": "QA Test API Key",
                "description": "Created during QA testing",
                "expires_in_days": 30
            },
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
            timeout=10
        )

        if response.status_code == 201:
            api_key_data = response.json()
            if "key" in api_key_data:
                log_test(TestResult("Auth", "API Key Creation", "PASS",
                                  {"key_id": api_key_data.get("id"),
                                   "key_prefix": api_key_data.get("key_prefix")}))
                test_user["api_key"] = api_key_data["key"]
                test_user["api_key_id"] = api_key_data.get("id")
            else:
                log_test(TestResult("Auth", "API Key Creation", "FAIL",
                                  {"missing_key": api_key_data}, "HIGH"))
        else:
            log_test(TestResult("Auth", "API Key Creation", "FAIL",
                              {"status_code": response.status_code}, "MEDIUM"))
    except Exception as e:
        log_test(TestResult("Auth", "API Key Creation", "ERROR", {"error": str(e)}, "MEDIUM"))

    # Test 2.9: List API keys
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
            timeout=10
        )

        if response.status_code == 200:
            api_keys = response.json()
            if isinstance(api_keys, list):
                log_test(TestResult("Auth", "List API Keys", "PASS",
                                  {"count": len(api_keys)}))
            else:
                log_test(TestResult("Auth", "List API Keys", "FAIL",
                                  {"unexpected_response": api_keys}, "MEDIUM"))
        else:
            log_test(TestResult("Auth", "List API Keys", "FAIL",
                              {"status_code": response.status_code}, "MEDIUM"))
    except Exception as e:
        log_test(TestResult("Auth", "List API Keys", "ERROR", {"error": str(e)}, "MEDIUM"))

# ============================================================================
# TEST SUITE 3: META-ANALYSIS WORKFLOW
# ============================================================================

def test_meta_analysis_workflow():
    """Test meta-analysis endpoints."""
    print("\n" + "="*80)
    print("TEST SUITE 3: META-ANALYSIS WORKFLOW")
    print("="*80)

    # First, login to get token
    timestamp = int(time.time())
    test_user = {
        "email": f"qa_workflow_{timestamp}@example.com",
        "password": "TestPass123!",
        "full_name": "QA Workflow User",
        "institution": "Test University"
    }

    # Register
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=test_user, timeout=10)
        if response.status_code != 201:
            print("⚠️  Skipping workflow tests - registration failed")
            return
    except Exception as e:
        print(f"⚠️  Skipping workflow tests - registration error: {e}")
        return

    # Login
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={"username": test_user["email"], "password": test_user["password"]},
            timeout=10
        )
        if response.status_code != 200:
            print("⚠️  Skipping workflow tests - login failed")
            return
        test_user["access_token"] = response.json()["access_token"]
    except Exception as e:
        print(f"⚠️  Skipping workflow tests - login error: {e}")
        return

    # Test 3.1: Create meta-analysis
    try:
        meta_analysis_request = {
            "research_question": "What is the effect of mindfulness-based interventions on anxiety in adults?",
            "topic": "Mindfulness and Anxiety",
            "inclusion_criteria": [
                "Randomized controlled trial",
                "Adult population (18+ years)",
                "Mindfulness-based intervention",
                "Anxiety as primary or secondary outcome"
            ],
            "exclusion_criteria": [
                "Non-English language",
                "Qualitative studies only",
                "Case studies or case reports"
            ],
            "databases": ["pubmed"],
            "peer_review_only": True
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/meta-analysis/create",
            json=meta_analysis_request,
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if "id" in result and "workflow" in result:
                log_test(TestResult("Meta-Analysis", "Create Meta-Analysis", "PASS",
                                  {"analysis_id": result.get("id"),
                                   "status": result.get("status")}))
                test_user["analysis_id"] = result.get("id")
            else:
                log_test(TestResult("Meta-Analysis", "Create Meta-Analysis", "FAIL",
                                  {"unexpected_response": result}, "HIGH"))
        else:
            log_test(TestResult("Meta-Analysis", "Create Meta-Analysis", "FAIL",
                              {"status_code": response.status_code, "response": response.text}, "CRITICAL"))
            log_bug("Meta-Analysis", "Cannot create meta-analysis",
                   f"Create endpoint returned {response.status_code}",
                   "CRITICAL",
                   [f"POST {BASE_URL}/api/v1/meta-analysis/create with valid request"],
                   "200 OK with analysis ID and workflow",
                   f"{response.status_code}: {response.text}")
            return
    except Exception as e:
        log_test(TestResult("Meta-Analysis", "Create Meta-Analysis", "ERROR",
                          {"error": str(e)}, "CRITICAL"))
        return

    # Test 3.2: Execute meta-analysis
    if "analysis_id" in test_user:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/meta-analysis/execute/{test_user['analysis_id']}",
                headers={"Authorization": f"Bearer {test_user['access_token']}"},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if "search_results" in result and "screening_results" in result:
                    log_test(TestResult("Meta-Analysis", "Execute Meta-Analysis", "PASS",
                                      {"total_found": result.get("search_results", {}).get("total_found"),
                                       "included": result.get("screening_results", {}).get("included")}))
                else:
                    log_test(TestResult("Meta-Analysis", "Execute Meta-Analysis", "FAIL",
                                      {"incomplete_results": result}, "HIGH"))
            else:
                log_test(TestResult("Meta-Analysis", "Execute Meta-Analysis", "FAIL",
                                  {"status_code": response.status_code}, "HIGH"))
                log_bug("Meta-Analysis", "Execution fails",
                       f"Execute endpoint returned {response.status_code}",
                       "HIGH",
                       [f"POST {BASE_URL}/api/v1/meta-analysis/execute/{{id}}"],
                       "200 OK with search and screening results",
                       f"{response.status_code}: {response.text}")
        except Exception as e:
            log_test(TestResult("Meta-Analysis", "Execute Meta-Analysis", "ERROR",
                              {"error": str(e)}, "HIGH"))

    # Test 3.3: Get status
    if "analysis_id" in test_user:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/meta-analysis/status/{test_user['analysis_id']}",
                headers={"Authorization": f"Bearer {test_user['access_token']}"},
                timeout=10
            )

            if response.status_code == 200:
                status = response.json()
                log_test(TestResult("Meta-Analysis", "Get Status", "PASS",
                                  {"status": status.get("status")}))
            else:
                log_test(TestResult("Meta-Analysis", "Get Status", "FAIL",
                                  {"status_code": response.status_code}, "MEDIUM"))
        except Exception as e:
            log_test(TestResult("Meta-Analysis", "Get Status", "ERROR",
                              {"error": str(e)}, "MEDIUM"))

    # Test 3.4: Ask question
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/meta-analysis/ask",
            json={
                "question": "How many studies were included in this meta-analysis?",
                "meta_analysis_id": test_user.get("analysis_id")
            },
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
            timeout=30
        )

        if response.status_code == 200:
            qa_result = response.json()
            if "answer" in qa_result:
                log_test(TestResult("Meta-Analysis", "QA System", "PASS",
                                  {"confidence": qa_result.get("confidence")}))
            else:
                log_test(TestResult("Meta-Analysis", "QA System", "FAIL",
                                  {"missing_answer": qa_result}, "MEDIUM"))
        else:
            log_test(TestResult("Meta-Analysis", "QA System", "FAIL",
                              {"status_code": response.status_code}, "MEDIUM"))
    except Exception as e:
        log_test(TestResult("Meta-Analysis", "QA System", "ERROR",
                          {"error": str(e)}, "MEDIUM"))

    # Test 3.5: Get audit trail
    if "analysis_id" in test_user:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/meta-analysis/audit/{test_user['analysis_id']}",
                headers={"Authorization": f"Bearer {test_user['access_token']}"},
                timeout=10
            )

            if response.status_code == 200:
                audit = response.json()
                log_test(TestResult("Meta-Analysis", "Audit Trail", "PASS",
                                  {"events": len(audit) if isinstance(audit, list) else "N/A"}))
            else:
                log_test(TestResult("Meta-Analysis", "Audit Trail", "FAIL",
                                  {"status_code": response.status_code}, "MEDIUM"))
        except Exception as e:
            log_test(TestResult("Meta-Analysis", "Audit Trail", "ERROR",
                              {"error": str(e)}, "MEDIUM"))

    # Test 3.6: Get report
    if "analysis_id" in test_user:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/meta-analysis/report/{test_user['analysis_id']}",
                headers={"Authorization": f"Bearer {test_user['access_token']}"},
                timeout=10
            )

            if response.status_code == 200:
                report = response.json()
                log_test(TestResult("Meta-Analysis", "Generate Report", "PASS",
                                  {"format": report.get("format")}))
            else:
                log_test(TestResult("Meta-Analysis", "Generate Report", "FAIL",
                                  {"status_code": response.status_code}, "MEDIUM"))
        except Exception as e:
            log_test(TestResult("Meta-Analysis", "Generate Report", "ERROR",
                              {"error": str(e)}, "MEDIUM"))

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def generate_report():
    """Generate comprehensive test report."""
    print("\n" + "="*80)
    print("COMPREHENSIVE QA AUDIT REPORT")
    print("="*80)

    # Summary statistics
    total_tests = len(TEST_RESULTS)
    passed = sum(1 for t in TEST_RESULTS if t.status == "PASS")
    failed = sum(1 for t in TEST_RESULTS if t.status == "FAIL")
    errors = sum(1 for t in TEST_RESULTS if t.status == "ERROR")
    warnings = sum(1 for t in TEST_RESULTS if t.status == "WARN")

    print(f"\nTest Execution Summary:")
    print(f"  Total Tests: {total_tests}")
    print(f"  ✓ Passed: {passed}")
    print(f"  ✗ Failed: {failed}")
    print(f"  ⚠  Warnings: {warnings}")
    print(f"  ❌ Errors: {errors}")
    print(f"  Success Rate: {(passed/total_tests*100):.1f}%")

    # Bug summary
    print(f"\nBugs Found: {len(BUG_REPORTS)}")
    critical_bugs = sum(1 for b in BUG_REPORTS if b["severity"] == "CRITICAL")
    high_bugs = sum(1 for b in BUG_REPORTS if b["severity"] == "HIGH")
    medium_bugs = sum(1 for b in BUG_REPORTS if b["severity"] == "MEDIUM")
    low_bugs = sum(1 for b in BUG_REPORTS if b["severity"] == "LOW")

    print(f"  🔴 CRITICAL: {critical_bugs}")
    print(f"  🟠 HIGH: {high_bugs}")
    print(f"  🟡 MEDIUM: {medium_bugs}")
    print(f"  🟢 LOW: {low_bugs}")

    # Production readiness verdict
    print("\n" + "="*80)
    print("PRODUCTION READINESS VERDICT")
    print("="*80)

    if critical_bugs > 0:
        print("\n❌ NOT PRODUCTION READY")
        print(f"   Reason: {critical_bugs} CRITICAL bug(s) must be fixed")
    elif high_bugs > 3:
        print("\n⚠️  CAUTION: CONDITIONAL APPROVAL")
        print(f"   Reason: {high_bugs} HIGH severity bugs found")
        print("   Recommendation: Fix high-priority bugs before full production release")
    elif failed > total_tests * 0.2:
        print("\n⚠️  CAUTION: LOW TEST PASS RATE")
        print(f"   Reason: Only {(passed/total_tests*100):.1f}% tests passing")
        print("   Recommendation: Investigate and fix failing tests")
    else:
        print("\n✅ PRODUCTION READY")
        print("   All critical systems operational")
        print("   Minor issues can be addressed in follow-up releases")

    # Save detailed reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save test results
    test_report_file = f"/Users/brandon/meta-analysis-tool/qa_audit_results_{timestamp}.json"
    with open(test_report_file, 'w') as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "warnings": warnings,
                "success_rate": passed/total_tests*100
            },
            "tests": [t.to_dict() for t in TEST_RESULTS]
        }, f, indent=2)
    print(f"\n📄 Test results saved to: {test_report_file}")

    # Save bug reports
    if BUG_REPORTS:
        bug_report_file = f"/Users/brandon/meta-analysis-tool/qa_bug_report_{timestamp}.json"
        with open(bug_report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_bugs": len(BUG_REPORTS),
                    "critical": critical_bugs,
                    "high": high_bugs,
                    "medium": medium_bugs,
                    "low": low_bugs
                },
                "bugs": BUG_REPORTS
            }, f, indent=2)
        print(f"🐛 Bug report saved to: {bug_report_file}")

    print("\n" + "="*80)

if __name__ == "__main__":
    print("="*80)
    print("META-ANALYSIS RESEARCH PLATFORM - COMPREHENSIVE QA AUDIT")
    print("="*80)
    print(f"Target: {BASE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Auditor: QA Engineer Agent")
    print("="*80)

    try:
        # Execute all test suites
        test_health_endpoints()
        test_authentication()
        test_meta_analysis_workflow()

        # Generate final report
        generate_report()

        # Exit code based on critical bugs
        critical_bugs = sum(1 for b in BUG_REPORTS if b["severity"] == "CRITICAL")
        sys.exit(1 if critical_bugs > 0 else 0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        generate_report()
        sys.exit(1)
