---
name: API Integration Helper
description: AI-powered API integration toolkit for endpoint mapping, schema validation, authentication management, and rate limiting analysis. Maps endpoints from code, validates JSON schemas, detects auth schemes, and analyzes rate limiting strategies.
version: 1.0.0
author: Skill Builder
tags:
  - api
  - integration
  - schema-validation
  - authentication
  - rate-limiting
  - openapi

activation_triggers:
  - keyword: "analyze api"
  - keyword: "validate schema"
  - keyword: "rate limit"
  - pattern: "endpoint_mapping|auth_detection|rate_limiting"
  - intent: "integrate_api"

parameters:
  - name: api_input
    type: string
    required: true
    description: "API code, OpenAPI spec, or request headers"
    example: "@app.get('/users/{id}')"
  
  - name: analysis_type
    type: string
    required: true
    enum: ["endpoint_mapping", "schema_validation", "auth_detection", "rate_limit_analysis"]
    description: "Type of API analysis to perform"
    example: "endpoint_mapping"
  
  - name: framework
    type: string
    required: false
    enum: ["flask", "fastapi", "django", "express", "openapi"]
    description: "API framework or specification format"
    example: "fastapi"
  
  - name: auth_type
    type: string
    required: false
    enum: ["basic", "bearer", "api_key", "oauth2", "hmac", "jwt"]
    description: "Authentication scheme to validate"
    example: "bearer"

scripts:
  - name: endpoint_mapper
    type: python
    path: scripts/endpoint_mapper.py
    description: "Maps and analyzes API endpoints from code or OpenAPI specs"
    confidence: "94%"
    params: ["api_input", "framework"]
  
  - name: schema_validator
    type: python
    path: scripts/schema_validator.py
    description: "Validates JSON schemas and request/response bodies"
    confidence: "92%"
    params: ["api_input", "analysis_type"]
  
  - name: auth_handler
    type: python
    path: scripts/auth_handler.py
    description: "Detects and validates API authentication schemes"
    confidence: "93%"
    params: ["auth_type"]
  
  - name: rate_limiter
    type: python
    path: scripts/rate_limiter.py
    description: "Analyzes rate limiting headers and strategies"
    confidence: "90%"
    params: ["analysis_type"]

capabilities:
  - Endpoint mapping from Flask/FastAPI/Django/Express code
  - OpenAPI specification parsing and analysis
  - JSON schema validation and generation
  - Request/response body validation
  - Authentication scheme detection (Basic, Bearer, OAuth2, JWT, HMAC, API Key)
  - Rate limit header detection (X-RateLimit, RateLimit standards)
  - Rate limiting strategy analysis
  - Client code generation (Python, JavaScript, TypeScript)
  - Security risk analysis for authentication
  - API schema comparison and compatibility checking

cache: true
composable: true

security_considerations:
  - Never log authentication credentials
  - Validate all API inputs before processing
  - Implement rate limiting on validation endpoints
  - Use HTTPS for all API communications
  - Sanitize error messages to avoid information disclosure
  - Implement proper CORS policies
  - Validate OpenAPI specs from untrusted sources
  - Store API keys securely (environment variables only)
---

## Usage Examples

### Endpoint Mapping
```python
from scripts.endpoint_mapper import EndpointMapper

mapper = EndpointMapper()
endpoints = mapper.analyze_fastapi_code("""
@app.get('/users/{id}')
@app.post('/users')
""")
print(f"Found {len(endpoints)} endpoints")
```

### Schema Validation
```python
from scripts.schema_validator import SchemaValidator

validator = SchemaValidator()
result = validator.validate_json_schema({
    "type": "object",
    "properties": {"name": {"type": "string"}}
})
print(f"Valid: {result['is_valid']}")
```

### Authentication Detection
```python
from scripts.auth_handler import AuthHandler

auth = AuthHandler()
detected = auth.detect_auth_scheme({
    "Authorization": "Bearer token123",
    "X-API-Key": "key456"
})
print(f"Auth types: {detected['auth_types']}")
```

### Rate Limit Analysis
```python
from scripts.rate_limiter import RateLimiter

limiter = RateLimiter()
analysis = limiter.analyze_rate_limits({
    "X-RateLimit-Limit": "1000",
    "X-RateLimit-Remaining": "999"
})
print(f"Requests remaining: {analysis['remaining']}")
```

## Output Format

All modules return structured JSON:

```json
{
  "analysis_type": "string",
  "endpoints_found": number,
  "authentication_schemes": ["array"],
  "validation_status": "valid|invalid|warning",
  "rate_limit_info": { "limit": number, "remaining": number },
  "security_score": 0-100,
  "recommendations": ["array of actionable items"],
  "client_code_generated": boolean
}
```

## Severity Levels

| Level | Meaning | Impact | Action |
|-------|---------|--------|--------|
| CRITICAL | Security vulnerability in auth/schema | High risk | Fix immediately |
| HIGH | Missing rate limit handling | Moderate risk | Implement within sprint |
| MEDIUM | Schema validation issue | Low-moderate risk | Plan improvement |
| LOW | Minor API consistency issue | Low risk | Consider for future |

## Version & Support

- **Version**: 1.0.0
- **Released**: February 2026
- **Status**: Production Ready
- **Confidence**: 92%

## Future Enhancements (v1.1.0)

- GraphQL API support
- gRPC endpoint mapping
- Webhook validation
- API versioning detection
- Mock server generation
- Integration with API gateway tools
- Automated SDK generation
- GraphQL schema analysis
