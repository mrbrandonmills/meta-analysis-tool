#!/bin/bash

# Performance Benchmarking Script
# Tests: Response times, concurrent requests, throughput

API="https://meta-analysis-tool-production.up.railway.app"

echo "========================================"
echo "  PERFORMANCE BENCHMARK"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Performance thresholds (milliseconds)
EXCELLENT=200
GOOD=500
ACCEPTABLE=1000

# Test 1: Health Check Response Time
echo "Test 1: Health Check Response Time"
echo "----------------------------------------"

TIMES=()
for i in {1..10}; do
  TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API/api/v1/health")
  TIME_MS=$(echo "$TIME * 1000" | bc)
  TIMES+=($TIME_MS)
  echo "Request $i: ${TIME_MS} ms"
done

# Calculate average
TOTAL=0
for t in "${TIMES[@]}"; do
  TOTAL=$(echo "$TOTAL + $t" | bc)
done
AVG=$(echo "$TOTAL / ${#TIMES[@]}" | bc)

echo ""
echo "Average Response Time: ${AVG} ms"

if [ $(echo "$AVG < $EXCELLENT" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ EXCELLENT${NC} (< ${EXCELLENT}ms)"
elif [ $(echo "$AVG < $GOOD" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ GOOD${NC} (< ${GOOD}ms)"
elif [ $(echo "$AVG < $ACCEPTABLE" | bc) -eq 1 ]; then
  echo -e "${YELLOW}⚠️  ACCEPTABLE${NC} (< ${ACCEPTABLE}ms)"
else
  echo -e "${RED}❌ SLOW${NC} (> ${ACCEPTABLE}ms)"
fi
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint Response Time"
echo "----------------------------------------"

ROOT_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API/")
ROOT_MS=$(echo "$ROOT_TIME * 1000" | bc)

echo "Response Time: ${ROOT_MS} ms"
if [ $(echo "$ROOT_MS < $GOOD" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ GOOD${NC}"
else
  echo -e "${YELLOW}⚠️  REVIEW${NC}"
fi
echo ""

# Test 3: API Documentation Load Time
echo "Test 3: API Documentation Load Time"
echo "----------------------------------------"

DOCS_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API/docs")
DOCS_MS=$(echo "$DOCS_TIME * 1000" | bc)

echo "Response Time: ${DOCS_MS} ms"
if [ $(echo "$DOCS_MS < 2000" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ GOOD${NC}"
else
  echo -e "${YELLOW}⚠️  REVIEW${NC}"
fi
echo ""

# Test 4: Authentication Flow Performance
echo "Test 4: Authentication Flow Performance"
echo "----------------------------------------"

TIMESTAMP=$(date +%s)
TEST_EMAIL="perf_${TIMESTAMP}@example.com"

# Registration
REG_START=$(date +%s%N)
curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"Test123!\",\"full_name\":\"Perf Test\",\"institution\":\"Test\"}" \
  > /dev/null
REG_END=$(date +%s%N)
REG_TIME=$(echo "($REG_END - $REG_START) / 1000000" | bc)

echo "Registration: ${REG_TIME} ms"

# Login
LOGIN_START=$(date +%s%N)
curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=Test123!" \
  > /dev/null
LOGIN_END=$(date +%s%N)
LOGIN_TIME=$(echo "($LOGIN_END - $LOGIN_START) / 1000000" | bc)

echo "Login: ${LOGIN_TIME} ms"

TOTAL_AUTH=$(echo "$REG_TIME + $LOGIN_TIME" | bc)
echo "Total Auth Flow: ${TOTAL_AUTH} ms"

if [ $(echo "$TOTAL_AUTH < 2000" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ EXCELLENT${NC}"
else
  echo -e "${YELLOW}⚠️  REVIEW${NC}"
fi
echo ""

# Test 5: Concurrent Requests
echo "Test 5: Concurrent Requests (10 parallel)"
echo "----------------------------------------"

CONCURRENT_START=$(date +%s%N)

for i in {1..10}; do
  curl -s "$API/api/v1/health" > /dev/null &
done

wait

CONCURRENT_END=$(date +%s%N)
CONCURRENT_TIME=$(echo "($CONCURRENT_END - $CONCURRENT_START) / 1000000" | bc)

echo "Time to complete 10 parallel requests: ${CONCURRENT_TIME} ms"
AVG_CONCURRENT=$(echo "$CONCURRENT_TIME / 10" | bc)
echo "Average per request: ${AVG_CONCURRENT} ms"

if [ $(echo "$CONCURRENT_TIME < 3000" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ EXCELLENT${NC} (handles concurrency well)"
else
  echo -e "${YELLOW}⚠️  REVIEW${NC} (concurrency may be bottleneck)"
fi
echo ""

# Test 6: Agents List Performance
echo "Test 6: Agents List Response Time"
echo "----------------------------------------"

AGENTS_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API/api/v1/agents/available")
AGENTS_MS=$(echo "$AGENTS_TIME * 1000" | bc)

echo "Response Time: ${AGENTS_MS} ms"
if [ $(echo "$AGENTS_MS < $GOOD" | bc) -eq 1 ]; then
  echo -e "${GREEN}✅ GOOD${NC}"
else
  echo -e "${YELLOW}⚠️  REVIEW${NC}"
fi
echo ""

# Summary
echo "========================================"
echo "  PERFORMANCE SUMMARY"
echo "========================================"
echo ""
echo "Endpoint Performance:"
echo "  Health Check:      ${AVG} ms avg"
echo "  Root Endpoint:     ${ROOT_MS} ms"
echo "  Documentation:     ${DOCS_MS} ms"
echo "  Auth Flow:         ${TOTAL_AUTH} ms"
echo "  Agents List:       ${AGENTS_MS} ms"
echo ""
echo "Concurrency:"
echo "  10 Parallel:       ${CONCURRENT_TIME} ms total"
echo "  Avg per request:   ${AVG_CONCURRENT} ms"
echo ""

# Overall rating
CRITICAL_SLOW=0

if [ $(echo "$AVG > $ACCEPTABLE" | bc) -eq 1 ]; then
  CRITICAL_SLOW=$((CRITICAL_SLOW + 1))
fi

if [ $(echo "$TOTAL_AUTH > 3000" | bc) -eq 1 ]; then
  CRITICAL_SLOW=$((CRITICAL_SLOW + 1))
fi

if [ $CRITICAL_SLOW -eq 0 ]; then
  echo -e "${GREEN}⚡ PERFORMANCE RATING: EXCELLENT${NC}"
  echo "All endpoints respond quickly under load."
elif [ $CRITICAL_SLOW -eq 1 ]; then
  echo -e "${YELLOW}⚠️  PERFORMANCE RATING: GOOD${NC}"
  echo "Some endpoints could be optimized."
else
  echo -e "${RED}⚠️  PERFORMANCE RATING: NEEDS OPTIMIZATION${NC}"
  echo "Multiple slow endpoints detected."
fi

echo ""
echo "Recommendations:"
echo "  < 200ms:  Excellent"
echo "  < 500ms:  Good"
echo "  < 1000ms: Acceptable"
echo "  > 1000ms: Review and optimize"
echo ""
