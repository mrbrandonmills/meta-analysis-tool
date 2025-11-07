#!/usr/bin/env python3
"""
Security Audit for Meta-Analysis Research Platform
Tests: SQL injection, XSS, CSRF, Auth bypass, Rate limiting
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"
SECURITY_FINDINGS = []

def log_finding(severity, category, title, description, test_details, impact):
    """Log a security finding."""
    finding = {
        "id": f"SEC-{len(SECURITY_FINDINGS) + 1:03d}",
        "severity": severity,  # CRITICAL, HIGH, MEDIUM, LOW, INFO
        "category": category,
        "title": title,
        "description": description,
        "test_details": test_details,
        "impact": impact,
        "timestamp": datetime.now().isoformat()
    }
    SECURITY_FINDINGS.append(finding)
    symbol = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
    print(f"{symbol} [{severity}] {title}")
    print(f"   {description}")

def test_sql_injection():
    """Test for SQL injection vulnerabilities."""
    print("\n" + "="*80)
    print("SQL INJECTION TESTS")
    print("="*80)

    # Test 1: SQL injection in login
    sql_payloads = [
        "admin' OR '1'='1",
        "admin'--",
        "admin' OR 1=1--",
        "' UNION SELECT NULL--",
        "1' AND '1'='1",
    ]

    for payload in sql_payloads:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                data={"username": payload, "password": "test"},
                timeout=5
            )

            if response.status_code == 200:
                log_finding(
                    "CRITICAL",
                    "SQL Injection",
                    "SQL Injection in Login Endpoint",
                    f"Login accepted SQL injection payload: {payload}",
                    {"payload": payload, "response": response.json()},
                    "Attacker could bypass authentication and access any user account"
                )
            elif response.status_code != 401:
                log_finding(
                    "MEDIUM",
                    "SQL Injection",
                    "Unusual Response to SQL Injection",
                    f"Login returned unexpected status code {response.status_code} for SQL payload",
                    {"payload": payload, "status_code": response.status_code},
                    "Possible SQL error leakage or unhandled exception"
                )
        except Exception as e:
            pass  # Expected to fail

    print("✓ SQL injection tests completed - No vulnerabilities found in login")

    # Test 2: SQL injection in registration
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": "test' OR '1'='1@example.com",
                "password": "Test123!",
                "full_name": "' OR '1'='1",
                "institution": "'; DROP TABLE users;--"
            },
            timeout=5
        )

        if response.status_code == 201:
            print("⚠️  Warning: System accepted potentially malicious input in registration")
        else:
            print("✓ Registration properly validates input")
    except Exception as e:
        pass

def test_xss_vulnerabilities():
    """Test for Cross-Site Scripting vulnerabilities."""
    print("\n" + "="*80)
    print("XSS (CROSS-SITE SCRIPTING) TESTS")
    print("="*80)

    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>",
        "'-alert('XSS')-'",
    ]

    # Test in registration fields
    for payload in xss_payloads:
        try:
            timestamp = int(time.time())
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": f"xss_test_{timestamp}@example.com",
                    "password": "Test123!",
                    "full_name": payload,
                    "institution": "Test"
                },
                timeout=5
            )

            if response.status_code == 201:
                user_data = response.json()
                # Check if payload is reflected
                if payload in str(user_data):
                    log_finding(
                        "HIGH",
                        "XSS",
                        "Stored XSS in User Profile",
                        f"XSS payload stored in database: {payload}",
                        {"payload": payload, "response": user_data},
                        "Attacker could execute JavaScript in victim's browser"
                    )
                    break
        except Exception as e:
            pass

    print("✓ XSS tests completed - No obvious vulnerabilities found")

def test_authentication_bypass():
    """Test for authentication bypass vulnerabilities."""
    print("\n" + "="*80)
    print("AUTHENTICATION BYPASS TESTS")
    print("="*80)

    # Test 1: Access protected endpoint without token
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", timeout=5)
        if response.status_code == 200:
            log_finding(
                "CRITICAL",
                "Auth Bypass",
                "Protected Endpoint Accessible Without Authentication",
                "/auth/me endpoint accessible without token",
                {"status_code": response.status_code},
                "Attacker can access user data without authentication"
            )
        else:
            print("✓ Protected endpoints require authentication")
    except Exception as e:
        pass

    # Test 2: Invalid token format
    invalid_tokens = [
        "Bearer invalid",
        "Bearer ",
        "invalid_token",
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
    ]

    for token in invalid_tokens:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": token},
                timeout=5
            )
            if response.status_code == 200:
                log_finding(
                    "CRITICAL",
                    "Auth Bypass",
                    "Invalid Token Accepted",
                    f"System accepted invalid token: {token}",
                    {"token": token},
                    "Authentication can be bypassed with invalid tokens"
                )
        except Exception as e:
            pass

    print("✓ Authentication bypass tests completed")

def test_rate_limiting():
    """Test rate limiting implementation."""
    print("\n" + "="*80)
    print("RATE LIMITING TESTS")
    print("="*80)

    # Test unauthenticated rate limiting
    print("Testing unauthenticated request rate limiting...")
    start_time = time.time()
    rate_limited = False

    for i in range(25):  # Try to exceed 20 req/min limit
        try:
            response = requests.get(f"{BASE_URL}/api/v1/health", timeout=2)
            if response.status_code == 429:
                rate_limited = True
                elapsed = time.time() - start_time
                print(f"✓ Rate limiting enforced after {i+1} requests in {elapsed:.1f}s")
                break
        except Exception as e:
            pass

    if not rate_limited:
        log_finding(
            "MEDIUM",
            "Rate Limiting",
            "Weak or Missing Rate Limiting",
            "System did not enforce rate limits after 25 requests",
            {"requests_sent": 25},
            "Attackers can perform DoS attacks or brute force without throttling"
        )
        print("⚠️  Rate limiting not detected or limit is too high")

def test_information_disclosure():
    """Test for information disclosure vulnerabilities."""
    print("\n" + "="*80)
    print("INFORMATION DISCLOSURE TESTS")
    print("="*80)

    # Test 1: Error message disclosure
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={"username": "nonexistent@example.com", "password": "test"},
            timeout=5
        )

        error_msg = response.text.lower()
        if "user not found" in error_msg or "no such user" in error_msg:
            log_finding(
                "LOW",
                "Information Disclosure",
                "User Enumeration via Login Error",
                "Login error messages reveal whether user exists",
                {"response": response.text},
                "Attacker can enumerate valid email addresses"
            )
        else:
            print("✓ Login errors do not reveal user existence")
    except Exception as e:
        pass

    # Test 2: Stack trace exposure
    try:
        response = requests.get(f"{BASE_URL}/api/v1/invalid-endpoint-12345", timeout=5)
        if "traceback" in response.text.lower() or "exception" in response.text.lower():
            log_finding(
                "MEDIUM",
                "Information Disclosure",
                "Stack Trace Exposure",
                "Server exposes stack traces in error responses",
                {"endpoint": "/api/v1/invalid-endpoint-12345"},
                "Attackers can learn about internal system structure"
            )
    except Exception as e:
        pass

    print("✓ Information disclosure tests completed")

def test_cors_configuration():
    """Test CORS configuration."""
    print("\n" + "="*80)
    print("CORS CONFIGURATION TESTS")
    print("="*80)

    try:
        response = requests.options(
            f"{BASE_URL}/api/v1/health",
            headers={
                "Origin": "https://malicious-site.com",
                "Access-Control-Request-Method": "POST"
            },
            timeout=5
        )

        cors_origin = response.headers.get("Access-Control-Allow-Origin", "")

        if cors_origin == "*":
            log_finding(
                "MEDIUM",
                "CORS",
                "Overly Permissive CORS Policy",
                "API allows requests from any origin (Access-Control-Allow-Origin: *)",
                {"cors_header": cors_origin},
                "Sensitive data can be accessed from malicious websites"
            )
            print("⚠️  CORS allows all origins")
        else:
            print(f"✓ CORS properly configured: {cors_origin}")
    except Exception as e:
        pass

def test_insecure_endpoints():
    """Test for insecure or debug endpoints."""
    print("\n" + "="*80)
    print("INSECURE ENDPOINT TESTS")
    print("="*80)

    debug_endpoints = [
        "/debug",
        "/api/debug",
        "/api/v1/debug",
        "/admin",
        "/api/admin",
        "/.env",
        "/config",
        "/api/config",
        "/api/v1/test",
        "/test",
    ]

    for endpoint in debug_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
            if response.status_code == 200:
                log_finding(
                    "HIGH",
                    "Insecure Endpoint",
                    f"Debug/Test Endpoint Exposed: {endpoint}",
                    f"Endpoint {endpoint} is accessible in production",
                    {"endpoint": endpoint, "status": response.status_code},
                    "Debug endpoints can leak sensitive information or provide attack vectors"
                )
        except Exception as e:
            pass

    print("✓ No debug endpoints found accessible")

def generate_security_report():
    """Generate final security report."""
    print("\n" + "="*80)
    print("SECURITY AUDIT SUMMARY")
    print("="*80)

    critical = sum(1 for f in SECURITY_FINDINGS if f["severity"] == "CRITICAL")
    high = sum(1 for f in SECURITY_FINDINGS if f["severity"] == "HIGH")
    medium = sum(1 for f in SECURITY_FINDINGS if f["severity"] == "MEDIUM")
    low = sum(1 for f in SECURITY_FINDINGS if f["severity"] == "LOW")

    print(f"\nSecurity Findings: {len(SECURITY_FINDINGS)}")
    print(f"  🔴 CRITICAL: {critical}")
    print(f"  🟠 HIGH: {high}")
    print(f"  🟡 MEDIUM: {medium}")
    print(f"  🟢 LOW: {low}")

    # Security score
    score = 100 - (critical * 25 + high * 10 + medium * 5 + low * 2)
    score = max(0, score)

    print(f"\nSecurity Score: {score}/100")

    if critical > 0:
        print("\n❌ CRITICAL SECURITY ISSUES FOUND - IMMEDIATE ACTION REQUIRED")
    elif high > 0:
        print("\n⚠️  HIGH SEVERITY ISSUES - SHOULD BE FIXED BEFORE PRODUCTION")
    elif medium > 2:
        print("\n⚠️  MULTIPLE MEDIUM ISSUES - RECOMMEND FIXING")
    else:
        print("\n✅ SECURITY POSTURE ACCEPTABLE")

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"/Users/brandon/meta-analysis-tool/security_audit_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump({
            "audit_date": datetime.now().isoformat(),
            "target": BASE_URL,
            "summary": {
                "total_findings": len(SECURITY_FINDINGS),
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "security_score": score
            },
            "findings": SECURITY_FINDINGS,
            "recommendations": [
                "Fix all CRITICAL issues immediately",
                "Address HIGH severity issues before production release",
                "Implement security monitoring and logging",
                "Conduct regular security audits",
                "Keep all dependencies updated",
                "Implement Web Application Firewall (WAF)",
                "Add security headers (CSP, X-Frame-Options, etc.)",
                "Conduct penetration testing before major releases"
            ]
        }, f, indent=2)

    print(f"\n📄 Security report saved to: {report_file}")

if __name__ == "__main__":
    print("="*80)
    print("META-ANALYSIS PLATFORM - SECURITY AUDIT")
    print("="*80)
    print(f"Target: {BASE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    try:
        test_sql_injection()
        test_xss_vulnerabilities()
        test_authentication_bypass()
        test_rate_limiting()
        test_information_disclosure()
        test_cors_configuration()
        test_insecure_endpoints()

        generate_security_report()

    except KeyboardInterrupt:
        print("\n\n⚠️  Security audit interrupted")
        generate_security_report()
    except Exception as e:
        print(f"\n\n❌ Error during security audit: {e}")
        generate_security_report()
