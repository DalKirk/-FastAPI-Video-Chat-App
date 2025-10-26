#!/bin/bash

# Test script for FastAPI Chat API
# Usage: ./test-chat-api.sh

API_URL="https://fastapi-video-chat-app-production.up.railway.app"

echo "?? Testing FastAPI Chat API"
echo "=============================="
echo ""

# Test 1: Health Check
echo "1??  Testing /api/v1/chat/health..."
HEALTH_RESPONSE=$(curl -s "$API_URL/api/v1/chat/health")
echo "$HEALTH_RESPONSE" | python -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"

# Check if Claude is enabled
if echo "$HEALTH_RESPONSE" | grep -q '"claude_enabled": true'; then
    echo "? Claude AI is ENABLED"
else
    echo "? Claude AI is DISABLED - Check ANTHROPIC_API_KEY in Railway"
fi

echo ""
echo "2??  Testing /api/v1/chat (sending a message)..."
CHAT_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Say hello in one sentence",
    "conversation_history": []
  }')

echo "$CHAT_RESPONSE" | python -m json.tool 2>/dev/null || echo "$CHAT_RESPONSE"

# Check if response was successful
if echo "$CHAT_RESPONSE" | grep -q '"success": true'; then
    echo "? Chat endpoint is WORKING"
    echo "?? AI Response received:"
    echo "$CHAT_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['content'])" 2>/dev/null
else
    echo "? Chat endpoint FAILED"
fi

echo ""
echo "=============================="
echo "Test complete!"
