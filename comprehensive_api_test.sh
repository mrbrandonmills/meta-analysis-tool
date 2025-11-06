#!/bin/bash

echo "========================================="
echo "Comprehensive API Testing"
echo "Meta-Analysis Research Platform"
echo "========================================="
echo ""

BASE_URL="https://meta-analysis-tool-production.up.railway.app/api/v1"

echo "TEST 1: Health Check (Basic)"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "TEST 2: Health Check (Detailed)"
curl -s "$BASE_URL/health/detailed" | python3 -m json.tool
echo ""

echo "TEST 3: Available Agents"
curl -s "$BASE_URL/agents/available" | python3 -m json.tool | head -50
echo ""

echo "TEST 4: Agent List"
curl -s "$BASE_URL/agents/list" | python3 -m json.tool | head -30
echo ""

echo "TEST 5: Metrics"
curl -s "$BASE_URL/health/metrics" | python3 -m json.tool
echo ""

echo "TEST 6: Version Info"
curl -s "$BASE_URL/health/version" | python3 -m json.tool
echo ""

echo "========================================="
echo "Testing Complete"
echo "========================================="
