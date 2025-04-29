#!/bin/bash

# Health check script for SERP Keyword Research API
# Usage: ./health_check.sh [host] [port]

HOST=${1:-localhost}
PORT=${2:-8000}
ENDPOINT="http://${HOST}:${PORT}/health"

echo "Checking API health at $ENDPOINT..."

# Try to connect to the health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT)

if [ $response -eq 200 ]; then
    echo "✅ API is healthy (Status code: $response)"
    
    # Get detailed health information
    echo "Fetching detailed health information..."
    curl -s $ENDPOINT | jq .
    
    exit 0
else
    echo "❌ API health check failed (Status code: $response)"
    exit 1
fi 