# API Documentation

## Overview

The AI SERP Keyword Research Agent exposes a RESTful API that allows users to analyze search terms for Print-on-Demand (POD) graphic tees, extract SEO insights, and get actionable recommendations. This document provides a complete reference for integrating with the API.

## Base URL

```
https://api.example.com/v1
```

For local development:
```
http://localhost:8000/v1
```

## Authentication

All API endpoints require authentication using an API key provided in the request header:

```
X-API-Key: your_api_key_here
```

Contact the system administrator to obtain your API key. API keys are tied to specific rate limits and usage quotas.

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage:

- Standard tier: 100 requests per hour
- Premium tier: 500 requests per hour

When a rate limit is exceeded, the API will return a 429 status code with a `Retry-After` header indicating when to retry the request.

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests in the current period
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

## Endpoints

### Analyze Keyword

Analyzes a search term to extract SEO insights and generate recommendations for POD graphic tees.

**URL**: `/analyze`

**Method**: `POST`

**Authentication**: Required (X-API-Key header)

**Request Body**:
```json
{
  "search_term": "best dad ever shirt",
  "max_results": 10
}
```

**Parameters**:
- `search_term` (required): The search term to analyze (3-255 characters)
- `max_results` (optional): Maximum number of SERP results to analyze (1-100, default: 10)

**Success Response** (Code: 200):
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-04-10T12:34:56Z",
  "search_term": "best dad ever shirt",
  "intent_analysis": {
    "main_keyword": "dad graphic tee",
    "secondary_keywords": [
      {"text": "funny dad shirt", "relevance": 0.92, "frequency": 7},
      {"text": "father's day gift", "relevance": 0.85, "frequency": 5},
      {"text": "best dad t-shirt", "relevance": 0.83, "frequency": 4}
    ],
    "intent_type": "transactional",
    "confidence": 0.87,
    "signals": ["product pages dominate", "shopping ads present", "price indicators in titles"]
  },
  "serp_features": [
    {
      "feature_type": "shopping_ads",
      "position": 1,
      "data": {
        "count": 4,
        "products": ["Dad T-Shirt", "Father's Day Gift Tee", "Funny Dad Shirt"]
      }
    },
    {
      "feature_type": "image_pack",
      "position": 3,
      "data": {
        "count": 8,
        "sources": ["amazon.com", "etsy.com", "redbubble.com"]
      }
    }
  ],
  "market_gap": {
    "detected": true,
    "description": "Limited personalized dad shirts with profession themes",
    "opportunity_score": 0.78,
    "competition_level": 0.65,
    "related_keywords": ["profession dad shirt", "dad job title tee", "personalized father gift"]
  },
  "recommendations": {
    "recommendations": [
      {
        "tactic_type": "product_page_optimization",
        "description": "Create product pages targeting 'profession + dad shirt' keywords (e.g., 'teacher dad shirt', 'engineer dad shirt')",
        "priority": 1,
        "confidence": 0.85
      },
      {
        "tactic_type": "content_creation",
        "description": "Develop a gift guide content around 'best gifts for dads by profession'",
        "priority": 2,
        "confidence": 0.78
      },
      {
        "tactic_type": "feature_targeting",
        "description": "Optimize product images for Google image pack inclusion",
        "priority": 3,
        "confidence": 0.82
      }
    ],
    "intent_based": true,
    "market_gap_based": true
  }
}
```

**Error Responses**:
- Code 400: Invalid request
  ```json
  {
    "error": "validation_error",
    "message": "Search term must be between 3 and 255 characters",
    "details": {
      "search_term": ["String should have at least 3 characters"]
    }
  }
  ```
- Code 401: Unauthorized
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing API key"
  }
  ```
- Code 429: Rate limit exceeded
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 30 seconds",
    "retry_after": 30
  }
  ```
- Code 500: Server error
  ```json
  {
    "error": "server_error",
    "message": "An unexpected error occurred",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

### Submit Feedback

Submits feedback about analysis results, which helps improve the system.

**URL**: `/feedback`

**Method**: `POST`

**Authentication**: Required (X-API-Key header)

**Request Body**:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "rating": 4,
  "comments": "Good recommendations but missed some keywords",
  "helpful_recommendations": [1, 3],
  "was_market_gap_accurate": true
}
```

**Parameters**:
- `analysis_id` (required): UUID of the analysis to provide feedback for
- `rating` (required): Overall rating of the analysis (1-5)
- `comments` (optional): Text feedback about the analysis
- `helpful_recommendations` (optional): List of recommendation indices that were helpful
- `was_market_gap_accurate` (optional): Whether the market gap detection was accurate

**Success Response** (Code: 200):
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "feedback_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:
- Code 400: Invalid request
- Code 401: Unauthorized
- Code 404: Analysis ID not found
- Code 429: Rate limit exceeded
- Code 500: Server error

### Health Check

Provides information about the health and status of the API.

**URL**: `/health`

**Method**: `GET`

**Authentication**: None required

**Success Response** (Code: 200):
```json
{
  "status": "healthy",
  "timestamp": "2025-04-10T12:34:56Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "serp_api": "operational"
  },
  "uptime": 1209600
}
```

**Error Response**:
- Code 503: Service unavailable
  ```json
  {
    "status": "unhealthy",
    "timestamp": "2025-04-10T12:34:56Z",
    "dependencies": {
      "database": "connected",
      "redis": "error",
      "serp_api": "operational"
    },
    "errors": {
      "redis": "Connection refused"
    }
  }
  ```

## Error Codes and Messages

The API uses standard HTTP status codes and provides detailed error messages:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | validation_error | Request validation failed |
| 401 | unauthorized | Invalid or missing API key |
| 403 | forbidden | Insufficient permissions |
| 404 | not_found | Resource not found |
| 429 | rate_limit_exceeded | Rate limit exceeded |
| 500 | server_error | Unexpected server error |
| 503 | service_unavailable | Service temporarily unavailable |

## Testing the API

### Using cURL

```bash
# Analyze a search term
curl -X POST "https://api.example.com/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"search_term": "best dad ever shirt", "max_results": 10}'

# Submit feedback
curl -X POST "https://api.example.com/v1/feedback" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"analysis_id": "550e8400-e29b-41d4-a716-446655440000", "rating": 4, "comments": "Good recommendations"}'

# Check health
curl "https://api.example.com/v1/health"
```

### Using Python

```python
import requests
import json

# API configuration
API_URL = "https://api.example.com/v1"
API_KEY = "your_api_key_here"

# Analyze a search term
def analyze_keyword(search_term, max_results=10):
    response = requests.post(
        f"{API_URL}/analyze",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"search_term": search_term, "max_results": max_results}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Example usage
results = analyze_keyword("best dad ever shirt")
print(json.dumps(results, indent=2))
```

## Rate Limiting Best Practices

To avoid hitting rate limits:

1. Cache analysis results for frequently used search terms
2. Implement exponential backoff when receiving 429 responses
3. Batch analyze requests during off-peak hours for bulk processing
4. Monitor your usage with the rate limit headers

## Webhook Notifications (Coming Soon)

Future versions will support webhook notifications for long-running analyses:

```json
{
  "webhook_url": "https://your-server.com/webhook",
  "events": ["analysis.completed", "analysis.failed"]
}
```

## Changelog

### v1.0.0 (2025-04-10)
- Initial release with analyze, feedback, and health endpoints
- Added authentication and rate limiting
- Implemented error handling and validation

### v0.9.0 (2025-03-15)
- Beta release for early access partners
- Limited rate limits and feature set 