# API Integration Helper

AI-powered API integration toolkit for analyzing, validating, and managing APIs. Provides endpoint mapping, schema validation, authentication detection, and rate limiting analysis across Flask, FastAPI, Django, Express, and OpenAPI specifications.

## Overview

The API Integration Helper provides comprehensive API integration capabilities:

- **Endpoint Mapping** - Extracts endpoints from code or OpenAPI specs
- **Schema Validation** - Validates JSON schemas and request/response data
- **Authentication Analysis** - Detects and validates auth schemes (Basic, Bearer, OAuth2, JWT, HMAC, API Key)
- **Rate Limiting** - Analyzes rate limit headers and strategies
- **Client Code Generation** - Generates SDK code in Python/JavaScript/TypeScript

## Architecture

### 4-Module System

```
API Integration Helper
├── Endpoint Mapper (endpoint_mapper.py)
│   ├── Flask endpoint extraction
│   ├── FastAPI endpoint extraction
│   ├── Django URL mapping
│   ├── Express.js route extraction
│   ├── OpenAPI spec parsing
│   └── Client code generation
│
├── Schema Validator (schema_validator.py)
│   ├── JSON schema validation
│   ├── Request/response validation
│   ├── Schema comparison
│   ├── Sample data generation
│   ├── Auto-detection from data
│   └── OpenAPI schema generation
│
├── Auth Handler (auth_handler.py)
│   ├── Basic auth validation
│   ├── Bearer token validation
│   ├── API key validation
│   ├── OAuth2 support
│   ├── JWT validation
│   ├── HMAC support
│   ├── Security risk analysis
│   └── Documentation generation
│
└── Rate Limiter (rate_limiter.py)
    ├── Rate limit header detection
    ├── Strategy analysis (token bucket, sliding window, etc.)
    ├── Rate limit recommendations
    ├── Retry strategy calculation
    ├── Rate limiter code generation
    └── Burst/throttle analysis
```

## Features

### Endpoint Mapper
Discovers and catalogs API endpoints:
- **Framework Support**: Flask, FastAPI, Django, Express.js
- **OpenAPI Parsing**: Extract endpoints from OpenAPI/Swagger specs
- **Path Analysis**: Detects resource patterns, nesting levels, complexity
- **Versioning Detection**: Identifies API versioning strategy
- **Client Generation**: Generates SDK in Python/JavaScript/TypeScript

**Example:**
```python
mapper = EndpointMapper()

# Map Flask routes
result = mapper.map_from_code("""
@app.get('/users/<id>')
def get_user(id):
    return {"id": id}

@app.post('/users')
def create_user():
    return {"id": 1}
""", framework="flask")

# Returns: endpoint list, patterns, design recommendations
```

### Schema Validator
Validates and analyzes JSON schemas:
- **Schema Validation**: Checks JSON schema structure compliance
- **Data Validation**: Validates sample data against schema
- **Schema Comparison**: Detects breaking changes between versions
- **Auto-Detection**: Infers schema from sample data
- **OpenAPI Generation**: Creates OpenAPI schema definitions

**Example:**
```python
validator = SchemaValidator()

schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "pattern": "^[^@]+@[^@]+$"}
    },
    "required": ["id", "name", "email"]
}

result = validator.validate_json_schema(schema)
# Returns: validation score, issues, recommendations
```

### Auth Handler
Detects and validates authentication schemes:
- **Auto-Detection**: Identifies auth type from headers
- **Validation**: Validates credentials and configuration
- **Header Generation**: Creates auth headers for requests
- **Security Analysis**: Identifies auth-related security risks
- **Documentation**: Generates auth integration guides

**Example:**
```python
handler = AuthHandler()

# Detect auth from headers
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiI..."
}

result = handler.detect_auth_scheme(headers)
# Returns: detected schemes, confidence, recommendations

# Generate auth header
auth_header = handler.generate_auth_header(
    "bearer",
    {"token": "your-token"}
)
```

### Rate Limiter
Analyzes rate limiting strategies:
- **Header Detection**: Identifies rate limit info from response headers
- **Strategy Analysis**: Evaluates token bucket, sliding window, etc.
- **Recommendations**: Suggests optimal rate limits by API type
- **Retry Strategy**: Calculates exponential backoff
- **Code Generation**: Generates rate limiter implementations

**Example:**
```python
analyzer = RateLimiterAnalyzer()

# Detect rate limits from headers
headers = {
    "X-RateLimit-Limit": "100",
    "X-RateLimit-Remaining": "45",
    "X-RateLimit-Reset": "1640995200"
}

result = analyzer.detect_rate_limit_headers(headers)
# Returns: limits, utilization, reset time
```

## Supported Frameworks

### Code Analysis
- **Flask** - Python web framework
- **FastAPI** - Modern Python async framework
- **Django** - Full-stack Python framework
- **Express.js** - Node.js web framework

### API Specifications
- **OpenAPI 3.0** - REST API specification
- **Swagger 2.0** - Legacy API specification

### Authentication
- **Basic Auth** - Username/password
- **Bearer Tokens** - Token-based auth
- **API Keys** - Simple key validation
- **OAuth 2.0** - Authorization framework
- **JWT** - JSON Web Tokens
- **HMAC** - Signature-based auth

## Output Specifications

### Endpoint Mapping Result
```json
{
  "framework": "fastapi",
  "total_endpoints": 3,
  "endpoints": [
    {
      "path": "/users/{id}",
      "method": "GET",
      "resource": "users",
      "path_parameters": 1,
      "complexity": "MODERATE"
    }
  ],
  "pattern_analysis": {
    "total_resources": 2,
    "max_nesting_level": 3,
    "design_score": 85
  }
}
```

### Schema Validation Result
```json
{
  "is_valid": true,
  "validation_score": 92,
  "property_count": 5,
  "required_fields": 3,
  "issues": [],
  "recommendations": [
    "Add descriptions to all properties",
    "Define constraint ranges for numeric fields"
  ]
}
```

### Auth Detection Result
```json
{
  "detected_schemes": ["bearer", "jwt"],
  "primary_scheme": "jwt",
  "confidence_scores": {
    "jwt": 92,
    "bearer": 85
  },
  "security_score": 78,
  "risks": [
    {
      "risk": "No signature verification",
      "severity": "CRITICAL"
    }
  ]
}
```

### Rate Limit Analysis Result
```json
{
  "detected_limits": {
    "requests_per_window": 100,
    "requests_remaining": 45,
    "reset_in_seconds": 45
  },
  "utilization_percent": 55,
  "recommended_strategy": "token_bucket",
  "retry_strategy": {
    "should_retry": false,
    "reason": "Requests still available"
  }
}
```

## Usage Examples

### Complete API Integration Workflow

```python
from scripts.endpoint_mapper import EndpointMapper
from scripts.schema_validator import SchemaValidator
from scripts.auth_handler import AuthHandler
from scripts.rate_limiter import RateLimiterAnalyzer

# 1. Map endpoints
mapper = EndpointMapper()
endpoints = mapper.map_from_code(api_code, framework="fastapi")

# 2. Validate request schema
validator = SchemaValidator()
schema_result = validator.validate_json_schema(request_schema)

# 3. Detect authentication
handler = AuthHandler()
auth_result = handler.detect_auth_scheme(response_headers)

# 4. Analyze rate limiting
analyzer = RateLimiterAnalyzer()
rate_result = analyzer.detect_rate_limit_headers(response_headers)

print(f"API has {endpoints['total_endpoints']} endpoints")
print(f"Schema validation score: {schema_result['validation_score']}")
print(f"Auth scheme: {auth_result['primary_scheme']}")
print(f"Rate limit utilization: {rate_result['utilization_percent']}%")
```

### Generate API Client Code

```python
mapper = EndpointMapper()

# Generate Python client
python_client = mapper.generate_client_code(endpoints, language="python")
print(python_client["client"])

# Generate TypeScript client
ts_client = mapper.generate_client_code(endpoints, language="typescript")
print(ts_client["client"])
```

### Rate Limiting Strategy

```python
analyzer = RateLimiterAnalyzer()

# Get recommendations
recommendations = analyzer.recommend_rate_limits({
    "type": "public",
    "expected_concurrent_users": 1000,
    "request_complexity": "medium"
})

# Analyze strategy
strategy = analyzer.analyze_rate_limit_strategy(
    "token_bucket",
    {
        "capacity": 1000,
        "refill_rate": 100
    }
)
```

## Rate Limiting Strategies

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| **Token Bucket** | Burst-friendly APIs | Allows bursts, fair | More complex |
| **Sliding Window** | Strict limits | Accurate, fair | Memory intensive |
| **Fixed Window** | Simple quotas | Easy, low overhead | Boundary burst issue |
| **Leaky Bucket** | Smooth traffic | Consistent rate, queuing | Latency for requests |

## Authentication Standards

### Basic Auth
```bash
Authorization: Basic dXNlcjpwYXNz
```
⚠️ Always use HTTPS

### Bearer Token
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiI...
```

### API Key
```bash
X-API-Key: sk_test_1234567890abcdef
```

### OAuth 2.0
```bash
Authorization: Bearer access_token
```

### JWT
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Standards Compliance

### Rate Limit Headers

**IETF Standard**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

**W3C Standard**:
```
RateLimit-Limit: 100
RateLimit-Remaining: 45
RateLimit-Reset: 1640995200
```

### JSON Schema
- Draft 7 validation
- $ref resolution
- AllOf/anyOf/oneOf support

## Performance Characteristics

| Operation | Avg Time | Spec Size | Scalability |
|-----------|----------|-----------|-------------|
| Endpoint Mapping | 100-500ms | Any | O(n) |
| Schema Validation | 50-200ms | < 10KB | O(n) |
| Auth Detection | 10-50ms | < 1KB | O(1) |
| Rate Limit Analysis | 5-20ms | < 1KB | O(1) |

## Common Issues & Solutions

### Issue: "No Standard Rate Limit Headers"
**Solution**: Implement X-RateLimit-* or RateLimit-* headers
```python
response.headers["X-RateLimit-Limit"] = "100"
response.headers["X-RateLimit-Remaining"] = str(remaining)
response.headers["X-RateLimit-Reset"] = str(reset_time)
```

### Issue: "JWT with 'none' Algorithm"
**Solution**: Always specify algorithm (HS256, RS256, etc.)
```python
import jwt
token = jwt.encode(payload, secret, algorithm="HS256")
```

### Issue: "API Key in Query Parameter"
**Solution**: Move API key to header
```python
headers = {"X-API-Key": api_key}
response = requests.get(url, headers=headers)
```

### Issue: "No Rate Limit Headers Detected"
**Solution**: Add rate limit headers to API responses
```python
@app.after_request
def add_rate_limit_headers(response):
    response.headers["X-RateLimit-Limit"] = "100"
    return response
```

## Integration Examples

### With Requests Library
```python
from scripts.auth_handler import AuthHandler

handler = AuthHandler()
headers = handler.generate_auth_header("bearer", {"token": token})
response = requests.get(url, headers=headers)
```

### With FastAPI
```python
from fastapi import FastAPI, Header

app = FastAPI()

@app.get("/api/endpoint")
async def endpoint(authorization: str = Header(...)):
    # Handle authorization
    pass
```

### With OpenAPI
```python
mapper = EndpointMapper()
result = mapper.map_from_openapi(openapi_spec)
```

## Deployment & Configuration

### Environment Variables
```bash
API_KEY=your-api-key
API_SECRET=your-secret
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
AUTH_TYPE=bearer
```

### Docker Configuration
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## Limitations

- Code analysis limited to specified frameworks
- OpenAPI parsing for v3.0+ (Swagger 2.0 basic support)
- JWT validation without key verification (advisory only)
- Rate limit detection requires standard headers
- Authentication flow generation limited to common schemes

## Version & Support

- **Version**: 1.0.0
- **Last Updated**: 2024
- **Status**: Production Ready
- **Support**: Check repository issues and documentation

## Future Enhancements

- Postman collection import/export
- API Blueprint specification support
- GraphQL endpoint analysis
- API gateway integration (AWS, Kong)
- Real-time API monitoring
- Performance testing recommendations
- API version migration guides
- Automatic API documentation generation
