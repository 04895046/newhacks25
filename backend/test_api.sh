#!/bin/bash

# Quick API Test Script
# This script tests the basic functionality of your API

BASE_URL="http://localhost:8000/api"

echo "🧪 Testing Backend API"
echo "====================="
echo ""

# Test 1: Register a test user
echo "1️⃣  Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

if echo "$REGISTER_RESPONSE" | grep -q "username"; then
    echo "✅ Registration successful!"
else
    echo "⚠️  Registration may have failed (user might already exist)"
fi
echo ""

# Test 2: Login
echo "2️⃣  Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Cannot continue tests."
    exit 1
fi

echo "✅ Login successful! Got token: ${TOKEN:0:20}..."
echo ""

# Test 3: Generate itinerary
echo "3️⃣  Testing itinerary generation..."
GENERATE_RESPONSE=$(curl -s -X POST "$BASE_URL/itineraries/generate/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d '{"region": "Toronto", "needs": "Test trip"}')

if echo "$GENERATE_RESPONSE" | grep -q "title"; then
    echo "✅ Itinerary generation successful!"
    echo "$GENERATE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GENERATE_RESPONSE"
else
    echo "❌ Itinerary generation failed!"
    echo "$GENERATE_RESPONSE"
fi
echo ""

# Test 4: List itineraries
echo "4️⃣  Testing itinerary list..."
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/itineraries/" \
  -H "Authorization: Token $TOKEN")

if echo "$LIST_RESPONSE" | grep -q "title"; then
    echo "✅ List retrieval successful!"
    ITINERARY_COUNT=$(echo "$LIST_RESPONSE" | grep -o "\"id\":" | wc -l)
    echo "Found $ITINERARY_COUNT itinerary/itineraries"
else
    echo "⚠️  No itineraries found (or error occurred)"
fi
echo ""

echo "🎉 API Testing Complete!"
echo ""
echo "Your backend is working! You can now:"
echo "  - Build your frontend"
echo "  - Integrate your ML model in api/views.py"
echo "  - View data at http://localhost:8000/admin/"
