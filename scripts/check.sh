#!/usr/bin/env bash
set -e

BASE_URL="${APEX_BASE_URL:-http://127.0.0.1:8000}"
TOKEN="${APEX_AUTH_TOKEN:-change-this-token-before-exposing}"

echo "Checking Apex Mentor health..."
curl -s "${BASE_URL}/health" | python3 -m json.tool

echo "\nAdding a test concept..."
curl -s -X POST "${BASE_URL}/api/concepts" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "CIA triad",
    "topic": "CompTIA Security+ / Fundamentals",
    "question": "What does the CIA triad mean?",
    "answer": "Confidentiality, Integrity, and Availability.",
    "notes": "A core security model used to classify security goals.",
    "tags": "security+ fundamentals cia"
  }' | python3 -m json.tool

echo "\nSearching memory..."
curl -s -X POST "${BASE_URL}/api/search" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query":"CIA", "limit":5}' | python3 -m json.tool
