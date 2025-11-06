#!/usr/bin/env python3
"""
Comprehensive Production Readiness Test Suite
Meta-Analysis Platform - QA Engineer Testing
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
import sys

class ProductionReadinessTest:
    def __init__(self, base_url: str, frontend_url: str):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.test_results = []
        self.start_time = None
        self.access_token = None
        self.test_user_email = f"qa-test-{int(time.time())}@example.com"
        self.test_user_password = "TestPass123"
        self.test_user_name = "QA Test User"

    def log_test(self, category: str, test_name: str, status: str,
                 response_time: float = 0, details: str = "",
                 http_code: int = None, error: str = ""):
        """Log test result"""
        result = {
            "category": category,
            "test_name": test_name,
            "status": status,  # PASS, FAIL, DEGRADED, SKIP
            "response_time_ms": round(response_time * 1000, 2),
            "http_code": http_code,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        # Print immediate feedback
        status_symbol = {
            "PASS": "✓",
            "FAIL": "✗",
            "DEGRADED": "⚠",
            "SKIP": "○"
        }
        print(f"  {status_symbol.get(status, '?')} {test_name} [{status}] ({round(response_time * 1000, 2)}ms)")
        if error:
            print(f"      Error: {error}")
        if details:
            print(f"      Details: {details}")

    def make_request(self, method: str, endpoint: str,
                     headers: Dict = None, data: Dict = None,
                     timeout: int = 30) -> Tuple[requests.Response, float]:
        """Make HTTP request and measure response time"""
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}

        start = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response_time = time.time() - start
            return response, response_time
        except Exception as e:
            response_time = time.time() - start
            raise

    # ==================== Test Category 1: Health & Infrastructure ====================

    def test_health_basic(self):
        """Test basic health endpoint"""
        print("\n[1.1] Testing Basic Health Endpoint")
        try:
            response, response_time = self.make_request("GET", "/api/v1/health")

            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")

                if status == "healthy":
                    self.log_test("Health & Infrastructure", "Basic Health Check", "PASS",
                                response_time, f"Status: {status}", response.status_code)
                else:
                    self.log_test("Health & Infrastructure", "Basic Health Check", "DEGRADED",
                                response_time, f"Status: {status}", response.status_code)
            else:
                self.log_test("Health & Infrastructure", "Basic Health Check", "FAIL",
                            response_time, "", response.status_code,
                            f"Expected 200, got {response.status_code}")
        except Exception as e:
            self.log_test("Health & Infrastructure", "Basic Health Check", "FAIL",
                        0, "", None, str(e))

    def test_health_detailed(self):
        """Test detailed health endpoint with service checks"""
        print("\n[1.2] Testing Detailed Health Endpoint")
        try:
            response, response_time = self.make_request("GET", "/api/v1/health/detailed")

            if response.status_code == 200:
                data = response.json()
                checks = data.get("checks", {})

                # Check individual services
                db_status = checks.get("database", {}).get("status", "unknown")
                redis_status = checks.get("redis", {}).get("status", "unknown")
                celery_status = checks.get("celery", {}).get("status", "unknown")

                details = f"DB: {db_status}, Redis: {redis_status}, Celery: {celery_status}"

                # Determine overall status
                if db_status == "healthy" and redis_status == "healthy" and celery_status == "healthy":
                    status = "PASS"
                elif db_status == "healthy" and redis_status == "healthy":
                    status = "DEGRADED"  # Celery issues acceptable for now
                else:
                    status = "FAIL"

                self.log_test("Health & Infrastructure", "Detailed Health Check", status,
                            response_time, details, response.status_code)

                # Log individual service checks
                self._log_service_status("Database", db_status, response_time)
                self._log_service_status("Redis", redis_status, response_time)
                self._log_service_status("Celery", celery_status, response_time)

            else:
                self.log_test("Health & Infrastructure", "Detailed Health Check", "FAIL",
                            response_time, "", response.status_code,
                            f"Expected 200, got {response.status_code}")
        except Exception as e:
            self.log_test("Health & Infrastructure", "Detailed Health Check", "FAIL",
                        0, "", None, str(e))

    def _log_service_status(self, service_name: str, status: str, response_time: float):
        """Log individual service status"""
        if status == "healthy":
            test_status = "PASS"
        elif status == "degraded":
            test_status = "DEGRADED"
        else:
            test_status = "FAIL"

        self.log_test("Health & Infrastructure", f"{service_name} Status", test_status,
                     response_time, f"Service status: {status}", 200)

    def test_cors_headers(self):
        """Test CORS configuration"""
        print("\n[1.3] Testing CORS Headers")
        try:
            response, response_time = self.make_request("GET", "/api/v1/health",
                headers={"Origin": self.frontend_url})

            cors_header = response.headers.get("Access-Control-Allow-Origin")

            if cors_header:
                if cors_header == "*" or cors_header == self.frontend_url:
                    self.log_test("Health & Infrastructure", "CORS Configuration", "PASS",
                                response_time, f"CORS header: {cors_header}", response.status_code)
                else:
                    self.log_test("Health & Infrastructure", "CORS Configuration", "DEGRADED",
                                response_time, f"CORS header: {cors_header}", response.status_code,
                                "CORS might not allow frontend access")
            else:
                self.log_test("Health & Infrastructure", "CORS Configuration", "FAIL",
                            response_time, "No CORS headers found", response.status_code)
        except Exception as e:
            self.log_test("Health & Infrastructure", "CORS Configuration", "FAIL",
                        0, "", None, str(e))

    # ==================== Test Category 2: Authentication ====================

    def test_user_registration(self):
        """Test user registration"""
        print("\n[2.1] Testing User Registration")
        try:
            user_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": self.test_user_name
            }

            response, response_time = self.make_request("POST", "/api/v1/auth/register",
                                                       data=user_data)

            if response.status_code == 201:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test("Authentication", "User Registration", "PASS",
                                response_time, f"User ID: {data.get('id')}", response.status_code)
                else:
                    self.log_test("Authentication", "User Registration", "FAIL",
                                response_time, "Missing expected fields", response.status_code)
            elif response.status_code == 400 and "already registered" in response.text.lower():
                self.log_test("Authentication", "User Registration", "PASS",
                            response_time, "User already exists (acceptable)", response.status_code)
            else:
                self.log_test("Authentication", "User Registration", "FAIL",
                            response_time, response.text[:200], response.status_code)
        except Exception as e:
            self.log_test("Authentication", "User Registration", "FAIL",
                        0, "", None, str(e))

    def test_user_login(self):
        """Test user login and token generation"""
        print("\n[2.2] Testing User Login")
        try:
            # OAuth2 password flow uses form data with 'username' field
            url = f"{self.base_url}/api/v1/auth/login"
            login_data = {
                "username": self.test_user_email,  # OAuth2 uses 'username' not 'email'
                "password": self.test_user_password
            }

            start = time.time()
            response = requests.post(url, data=login_data, timeout=30)
            response_time = time.time() - start

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                token_type = data.get("token_type")

                if access_token and token_type:
                    self.access_token = access_token
                    self.log_test("Authentication", "User Login", "PASS",
                                response_time,
                                f"Token received (type: {token_type}, length: {len(access_token)})",
                                response.status_code)
                else:
                    self.log_test("Authentication", "User Login", "FAIL",
                                response_time, "Missing token fields", response.status_code)
            else:
                self.log_test("Authentication", "User Login", "FAIL",
                            response_time, response.text[:200], response.status_code)
        except Exception as e:
            self.log_test("Authentication", "User Login", "FAIL",
                        0, "", None, str(e))

    def test_token_authentication(self):
        """Test token authentication on protected endpoint"""
        print("\n[2.3] Testing Token Authentication")

        if not self.access_token:
            self.log_test("Authentication", "Token Authentication", "SKIP",
                        0, "No access token available", None)
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response, response_time = self.make_request("GET", "/api/v1/auth/me",
                                                       headers=headers)

            if response.status_code == 200:
                data = response.json()
                if "email" in data and data["email"] == self.test_user_email:
                    self.log_test("Authentication", "Token Authentication", "PASS",
                                response_time, f"User verified: {data.get('email')}",
                                response.status_code)
                else:
                    self.log_test("Authentication", "Token Authentication", "FAIL",
                                response_time, "User data mismatch", response.status_code)
            else:
                self.log_test("Authentication", "Token Authentication", "FAIL",
                            response_time, response.text[:200], response.status_code)
        except Exception as e:
            self.log_test("Authentication", "Token Authentication", "FAIL",
                        0, "", None, str(e))

    def test_unauthorized_access(self):
        """Test that protected endpoints reject unauthorized access"""
        print("\n[2.4] Testing Unauthorized Access Protection")
        try:
            response, response_time = self.make_request("GET", "/api/v1/auth/me")

            if response.status_code == 401:
                self.log_test("Authentication", "Unauthorized Access Protection", "PASS",
                            response_time, "Correctly rejected unauthorized request",
                            response.status_code)
            else:
                self.log_test("Authentication", "Unauthorized Access Protection", "FAIL",
                            response_time,
                            f"Expected 401, got {response.status_code}",
                            response.status_code)
        except Exception as e:
            self.log_test("Authentication", "Unauthorized Access Protection", "FAIL",
                        0, "", None, str(e))

    # ==================== Test Category 3: Meta-Analysis Workflow ====================

    def test_meta_analysis_creation(self):
        """Test meta-analysis creation endpoint"""
        print("\n[3.1] Testing Meta-Analysis Creation")

        if not self.access_token:
            self.log_test("Meta-Analysis Workflow", "Meta-Analysis Creation", "SKIP",
                        0, "No access token available", None)
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            meta_analysis_data = {
                "research_question": "What is the effect of exercise on depression?",
                "inclusion_criteria": ["randomized controlled trials", "depression diagnosis", "exercise intervention"],
                "exclusion_criteria": ["non-English studies", "case studies"],
                "databases": ["pubmed", "scopus"],
                "date_range": {
                    "start_date": "2015-01-01",
                    "end_date": "2024-12-31"
                }
            }

            response, response_time = self.make_request("POST", "/api/v1/meta-analysis/create",
                                                       headers=headers, data=meta_analysis_data)

            if response.status_code in [200, 201]:
                data = response.json()
                workflow_id = data.get("workflow_id") or data.get("id")

                if workflow_id:
                    self.log_test("Meta-Analysis Workflow", "Meta-Analysis Creation", "PASS",
                                response_time, f"Workflow ID: {workflow_id}", response.status_code)
                else:
                    self.log_test("Meta-Analysis Workflow", "Meta-Analysis Creation", "DEGRADED",
                                response_time, "Created but missing workflow ID", response.status_code)
            elif response.status_code == 503:
                self.log_test("Meta-Analysis Workflow", "Meta-Analysis Creation", "DEGRADED",
                            response_time,
                            "Service unavailable (likely Celery workers)",
                            response.status_code)
            else:
                self.log_test("Meta-Analysis Workflow", "Meta-Analysis Creation", "FAIL",
                            response_time, response.text[:200], response.status_code)
        except Exception as e:
            self.log_test("Meta-Analysis Workflow", "Meta-Analysis Creation", "FAIL",
                        0, "", None, str(e))

    def test_meta_analysis_list(self):
        """Test listing meta-analyses"""
        print("\n[3.2] Testing Meta-Analysis List")

        if not self.access_token:
            self.log_test("Meta-Analysis Workflow", "Meta-Analysis List", "SKIP",
                        0, "No access token available", None)
            return

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response, response_time = self.make_request("GET", "/api/v1/meta-analysis/list",
                                                       headers=headers)

            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else data.get("count", 0)
                self.log_test("Meta-Analysis Workflow", "Meta-Analysis List", "PASS",
                            response_time, f"Found {count} meta-analyses", response.status_code)
            else:
                self.log_test("Meta-Analysis Workflow", "Meta-Analysis List", "FAIL",
                            response_time, response.text[:200], response.status_code)
        except Exception as e:
            self.log_test("Meta-Analysis Workflow", "Meta-Analysis List", "FAIL",
                        0, "", None, str(e))

    # ==================== Test Category 4: API Endpoints ====================

    def test_api_documentation(self):
        """Test API documentation endpoint"""
        print("\n[4.1] Testing API Documentation")
        try:
            response, response_time = self.make_request("GET", "/docs")

            if response.status_code == 200:
                self.log_test("API Endpoints", "API Documentation", "PASS",
                            response_time, "Swagger UI accessible", response.status_code)
            else:
                self.log_test("API Endpoints", "API Documentation", "FAIL",
                            response_time, "", response.status_code)
        except Exception as e:
            self.log_test("API Endpoints", "API Documentation", "FAIL",
                        0, "", None, str(e))

    def test_openapi_spec(self):
        """Test OpenAPI specification endpoint"""
        print("\n[4.2] Testing OpenAPI Specification")
        try:
            response, response_time = self.make_request("GET", "/openapi.json")

            if response.status_code == 200:
                data = response.json()
                if "openapi" in data and "paths" in data:
                    path_count = len(data.get("paths", {}))
                    self.log_test("API Endpoints", "OpenAPI Specification", "PASS",
                                response_time, f"{path_count} endpoints documented",
                                response.status_code)
                else:
                    self.log_test("API Endpoints", "OpenAPI Specification", "FAIL",
                                response_time, "Invalid OpenAPI spec", response.status_code)
            else:
                self.log_test("API Endpoints", "OpenAPI Specification", "FAIL",
                            response_time, "", response.status_code)
        except Exception as e:
            self.log_test("API Endpoints", "OpenAPI Specification", "FAIL",
                        0, "", None, str(e))

    def test_error_handling_404(self):
        """Test 404 error handling"""
        print("\n[4.3] Testing 404 Error Handling")
        try:
            response, response_time = self.make_request("GET", "/api/v1/nonexistent-endpoint")

            if response.status_code == 404:
                self.log_test("API Endpoints", "404 Error Handling", "PASS",
                            response_time, "Correctly returned 404", response.status_code)
            else:
                self.log_test("API Endpoints", "404 Error Handling", "FAIL",
                            response_time, f"Expected 404, got {response.status_code}",
                            response.status_code)
        except Exception as e:
            self.log_test("API Endpoints", "404 Error Handling", "FAIL",
                        0, "", None, str(e))

    def test_error_handling_invalid_json(self):
        """Test invalid JSON handling"""
        print("\n[4.4] Testing Invalid JSON Handling")
        try:
            headers = {"Content-Type": "application/json"}
            url = f"{self.base_url}/api/v1/auth/register"

            start = time.time()
            response = requests.post(url, headers=headers, data="invalid json", timeout=30)
            response_time = time.time() - start

            if response.status_code in [400, 422]:
                self.log_test("API Endpoints", "Invalid JSON Handling", "PASS",
                            response_time, "Correctly rejected invalid JSON", response.status_code)
            else:
                self.log_test("API Endpoints", "Invalid JSON Handling", "FAIL",
                            response_time, f"Expected 400/422, got {response.status_code}",
                            response.status_code)
        except Exception as e:
            self.log_test("API Endpoints", "Invalid JSON Handling", "FAIL",
                        0, "", None, str(e))

    # ==================== Test Category 5: Performance & Load ====================

    def test_response_time_health(self):
        """Test health endpoint response time"""
        print("\n[5.1] Testing Health Endpoint Response Time")
        response_times = []

        try:
            for i in range(5):
                response, response_time = self.make_request("GET", "/api/v1/health")
                if response.status_code == 200:
                    response_times.append(response_time)

            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)

                if avg_time < 1.0:  # Under 1 second average
                    status = "PASS"
                elif avg_time < 3.0:  # Under 3 seconds
                    status = "DEGRADED"
                else:
                    status = "FAIL"

                self.log_test("Performance & Load", "Health Endpoint Response Time", status,
                            avg_time,
                            f"Avg: {round(avg_time*1000, 2)}ms, Min: {round(min_time*1000, 2)}ms, Max: {round(max_time*1000, 2)}ms",
                            200)
            else:
                self.log_test("Performance & Load", "Health Endpoint Response Time", "FAIL",
                            0, "No successful requests", None)
        except Exception as e:
            self.log_test("Performance & Load", "Health Endpoint Response Time", "FAIL",
                        0, "", None, str(e))

    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("\n[5.2] Testing Concurrent Request Handling")
        try:
            import concurrent.futures

            def make_health_request():
                try:
                    response, response_time = self.make_request("GET", "/api/v1/health")
                    return response.status_code == 200, response_time
                except:
                    return False, 0

            # Make 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                start = time.time()
                futures = [executor.submit(make_health_request) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                total_time = time.time() - start

            success_count = sum(1 for success, _ in results if success)
            avg_response_time = sum(rt for _, rt in results if rt > 0) / len(results) if results else 0

            if success_count == 10:
                self.log_test("Performance & Load", "Concurrent Request Handling", "PASS",
                            total_time,
                            f"10/10 requests succeeded, avg response: {round(avg_response_time*1000, 2)}ms",
                            200)
            elif success_count >= 7:
                self.log_test("Performance & Load", "Concurrent Request Handling", "DEGRADED",
                            total_time, f"{success_count}/10 requests succeeded", 200)
            else:
                self.log_test("Performance & Load", "Concurrent Request Handling", "FAIL",
                            total_time, f"Only {success_count}/10 requests succeeded", 200)
        except Exception as e:
            self.log_test("Performance & Load", "Concurrent Request Handling", "FAIL",
                        0, "", None, str(e))

    def test_database_performance(self):
        """Test database query performance via auth endpoint"""
        print("\n[5.3] Testing Database Performance")

        if not self.access_token:
            self.log_test("Performance & Load", "Database Performance", "SKIP",
                        0, "No access token available", None)
            return

        response_times = []
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}

            for i in range(5):
                response, response_time = self.make_request("GET", "/api/v1/auth/me",
                                                           headers=headers)
                if response.status_code == 200:
                    response_times.append(response_time)

            if response_times:
                avg_time = sum(response_times) / len(response_times)

                if avg_time < 0.5:  # Under 500ms
                    status = "PASS"
                elif avg_time < 2.0:  # Under 2 seconds
                    status = "DEGRADED"
                else:
                    status = "FAIL"

                self.log_test("Performance & Load", "Database Performance", status,
                            avg_time,
                            f"Average DB query time: {round(avg_time*1000, 2)}ms",
                            200)
            else:
                self.log_test("Performance & Load", "Database Performance", "FAIL",
                            0, "No successful requests", None)
        except Exception as e:
            self.log_test("Performance & Load", "Database Performance", "FAIL",
                        0, "", None, str(e))

    # ==================== Test Runner ====================

    def run_all_tests(self):
        """Run all production readiness tests"""
        self.start_time = time.time()

        print("=" * 70)
        print("PRODUCTION READINESS TEST SUITE")
        print("Meta-Analysis Platform - Comprehensive QA Testing")
        print("=" * 70)
        print(f"\nBackend URL: {self.base_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Test Start: {datetime.now().isoformat()}")
        print("=" * 70)

        # Category 1: Health & Infrastructure
        print("\n" + "=" * 70)
        print("CATEGORY 1: HEALTH & INFRASTRUCTURE TESTS")
        print("=" * 70)
        self.test_health_basic()
        self.test_health_detailed()
        self.test_cors_headers()

        # Category 2: Authentication
        print("\n" + "=" * 70)
        print("CATEGORY 2: AUTHENTICATION TESTS")
        print("=" * 70)
        self.test_user_registration()
        self.test_user_login()
        self.test_token_authentication()
        self.test_unauthorized_access()

        # Category 3: Meta-Analysis Workflow
        print("\n" + "=" * 70)
        print("CATEGORY 3: META-ANALYSIS WORKFLOW TESTS")
        print("=" * 70)
        self.test_meta_analysis_creation()
        self.test_meta_analysis_list()

        # Category 4: API Endpoints
        print("\n" + "=" * 70)
        print("CATEGORY 4: API ENDPOINT TESTS")
        print("=" * 70)
        self.test_api_documentation()
        self.test_openapi_spec()
        self.test_error_handling_404()
        self.test_error_handling_invalid_json()

        # Category 5: Performance & Load
        print("\n" + "=" * 70)
        print("CATEGORY 5: PERFORMANCE & LOAD TESTS")
        print("=" * 70)
        self.test_response_time_health()
        self.test_concurrent_requests()
        self.test_database_performance()

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time

        # Calculate statistics
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        degraded = sum(1 for r in self.test_results if r["status"] == "DEGRADED")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")

        # Calculate by category
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"PASS": 0, "FAIL": 0, "DEGRADED": 0, "SKIP": 0}
            categories[cat][result["status"]] += 1

        # Calculate average response times
        response_times = [r["response_time_ms"] for r in self.test_results if r["response_time_ms"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Determine overall status
        if failed == 0 and degraded == 0:
            overall_status = "GO"
            status_color = "GREEN"
        elif failed == 0 and degraded <= 2:
            overall_status = "GO WITH MONITORING"
            status_color = "YELLOW"
        elif failed <= 2 and degraded <= 3:
            overall_status = "NO-GO (FIXABLE)"
            status_color = "YELLOW"
        else:
            overall_status = "NO-GO (CRITICAL)"
            status_color = "RED"

        # Print summary
        print("\n" + "=" * 70)
        print("TEST EXECUTION SUMMARY")
        print("=" * 70)
        print(f"\nTotal Tests: {total_tests}")
        print(f"  ✓ Passed:   {passed} ({round(passed/total_tests*100, 1)}%)")
        print(f"  ✗ Failed:   {failed} ({round(failed/total_tests*100, 1)}%)")
        print(f"  ⚠ Degraded: {degraded} ({round(degraded/total_tests*100, 1)}%)")
        print(f"  ○ Skipped:  {skipped} ({round(skipped/total_tests*100, 1)}%)")
        print(f"\nExecution Time: {round(total_time, 2)}s")
        print(f"Average Response Time: {round(avg_response_time, 2)}ms")

        # Print category breakdown
        print("\n" + "-" * 70)
        print("CATEGORY BREAKDOWN")
        print("-" * 70)
        for cat, stats in categories.items():
            total_cat = sum(stats.values())
            print(f"\n{cat}:")
            print(f"  Pass: {stats['PASS']}/{total_cat}, Fail: {stats['FAIL']}/{total_cat}, "
                  f"Degraded: {stats['DEGRADED']}/{total_cat}, Skip: {stats['SKIP']}/{total_cat}")

        # Print failed tests
        if failed > 0:
            print("\n" + "-" * 70)
            print("FAILED TESTS")
            print("-" * 70)
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"\n✗ {result['test_name']} ({result['category']})")
                    print(f"  HTTP Code: {result['http_code']}")
                    print(f"  Error: {result['error']}")
                    if result['details']:
                        print(f"  Details: {result['details']}")

        # Print degraded tests
        if degraded > 0:
            print("\n" + "-" * 70)
            print("DEGRADED TESTS (Warnings)")
            print("-" * 70)
            for result in self.test_results:
                if result["status"] == "DEGRADED":
                    print(f"\n⚠ {result['test_name']} ({result['category']})")
                    print(f"  Details: {result['details']}")

        # Print production readiness assessment
        print("\n" + "=" * 70)
        print("PRODUCTION READINESS ASSESSMENT")
        print("=" * 70)
        print(f"\nOverall Status: [{status_color}] {overall_status}")

        if overall_status == "GO":
            print("\n🎉 Platform is production ready!")
            print("All tests passed. System is ready for board meeting demonstration.")
        elif overall_status == "GO WITH MONITORING":
            print("\n✓ Platform is functional with minor issues")
            print("Core features work but some degraded services need monitoring.")
            print("Recommendation: Proceed with board meeting, note limitations.")
        elif overall_status == "NO-GO (FIXABLE)":
            print("\n⚠ Platform has fixable issues")
            print("Some critical tests failed but issues appear fixable.")
            print("Recommendation: Fix issues before board meeting.")
        else:
            print("\n✗ Platform has critical issues")
            print("Multiple critical failures detected.")
            print("Recommendation: Do not proceed to board meeting until fixed.")

        # Save detailed results to JSON
        report_file = f"/Users/brandon/meta-analysis-tool/production_test_results_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "degraded": degraded,
                    "skipped": skipped,
                    "execution_time_seconds": round(total_time, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "overall_status": overall_status
                },
                "category_breakdown": categories,
                "detailed_results": self.test_results
            }, f, indent=2)

        print(f"\nDetailed results saved to: {report_file}")

        return overall_status


def main():
    # Configuration
    backend_url = "https://meta-analysis-tool-production.up.railway.app"
    frontend_url = "https://meta-analysis-tool.vercel.app"

    # Run tests
    tester = ProductionReadinessTest(backend_url, frontend_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
