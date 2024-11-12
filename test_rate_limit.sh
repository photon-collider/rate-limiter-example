#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api/example"  # Update with your endpoint
REQUESTS=20  # Number of requests to make
DELAY=0.01   # Delay between requests in seconds

# Text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo "Testing rate limits on $API_URL"
echo "Will make $REQUESTS requests with ${DELAY}s delay between them"
echo "----------------------------------------"

for i in $(seq 1 $REQUESTS); do
    echo -e "\nRequest $i:"
    
    # Make request and capture both response and headers
    response=$(curl -i -s -w "\n%{http_code}" $API_URL)
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract headers and body (everything except last line)
    headers_and_body=$(echo "$response" | sed \$d)
    
    # Check rate limit headers
    remaining=$(echo "$headers_and_body" | grep -i "X-RateLimit-Remaining" || echo "N/A")
    retry_after=$(echo "$headers_and_body" | grep -i "Retry-After" || echo "N/A")
    
    # Print status with color
    if [ $status_code -eq 200 ]; then
        echo -e "${GREEN}Status: $status_code${NC}"
    else
        echo -e "${RED}Status: $status_code${NC}"
    fi
    
    # Print rate limit info
    echo "Rate Limit Remaining: $remaining"
    if [[ $status_code -eq 429 ]]; then
        echo "Retry After: $retry_after"
    fi
    
    # Add delay between requests
    if [ $i -lt $REQUESTS ]; then
        echo "Waiting ${DELAY}s before next request..."
        sleep $DELAY
    fi
done

echo -e "\n----------------------------------------"
echo "Test completed!"