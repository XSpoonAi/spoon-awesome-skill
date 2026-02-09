---
name: API Documentation Generator
description: AI-powered API documentation generation tool that auto-generates comprehensive API docs from source code, including OpenAPI/Swagger specs, Postman collections, and markdown documentation with examples and authentication details.
version: 1.0.0
author: Skill Builder
tags:
  - api-documentation
  - openapi
  - swagger
  - postman
  - code-analysis
  - markdown
  - rest-api
  - documentation

activation_triggers:
  - keyword: "generate api docs"
  - keyword: "create documentation"
  - keyword: "openapi spec"
  - pattern: "api_documentation|swagger|postman_collection"
  - intent: "generate_api_documentation"

parameters:
  - name: source_code
    type: string
    required: true
    description: "API source code or existing documentation to analyze"
    example: "@app.get('/users/{id}')"
  
  - name: doc_format
    type: string
    required: true
    enum: ["openapi", "markdown", "postman", "html", "swagger"]
    description: "Output documentation format"
    example: "openapi"
  
  - name: framework
    type: string
    required: false
    enum: ["flask", "fastapi", "django", "express", "spring"]
    description: "API framework for context-aware generation"
    example: "fastapi"
  
  - name: include_examples
    type: boolean
    required: false
    default: true
    description: "Include request/response examples"
    example: true
  
  - name: auth_schemes
    type: array
    required: false
    description: "Authentication schemes to document"
    example: ["bearer", "api_key"]

scripts:
  - name: code_analyzer
    type: python
    path: scripts/code_analyzer.py
    description: "Analyzes API source code and extracts endpoints, parameters, and schemas"
    confidence: "94%"
    params: ["source_code", "framework"]
  
  - name: openapi_generator
    type: python
    path: scripts/openapi_generator.py
    description: "Generates OpenAPI 3.0 specifications with schemas and examples"
    confidence: "93%"
    params: ["doc_format", "include_examples"]
  
  - name: postman_generator
    type: python
    path: scripts/postman_generator.py
    description: "Creates Postman collections with pre-configured requests"
    confidence: "91%"
    params: ["auth_schemes", "include_examples"]
  
  - name: markdown_generator
    type: python
    path: scripts/markdown_generator.py
    description: "Generates markdown documentation with examples and usage guides"
    confidence: "92%"
    params: ["include_examples"]

capabilities:
  - Auto-generate OpenAPI 3.0 specifications
  - Create Postman collections with authentication
  - Generate markdown API documentation
  - Extract endpoints from Flask/FastAPI/Django/Express code
  - Parse request/response schemas automatically
  - Include authentication documentation (Bearer, API Key, OAuth2, JWT)
  - Generate code examples in multiple languages
  - Create interactive HTML documentation
  - Detect and document query parameters, path parameters, headers
  - Schema validation and type inference
  - Error response documentation
  - Rate limit documentation
  - Versioning support

cache: true
composable: true

security_considerations:
  - Sanitize source code before processing
  - Don't expose sensitive authentication credentials in examples
  - Validate generated OpenAPI specs for security issues
  - Redact API keys and tokens from generated documentation
  - Use placeholder values for sensitive data
  - Implement access control for documentation endpoints
  - Validate user inputs to prevent injection attacks
  - Ensure generated docs don't leak internal implementation details
---

## Usage Examples

### Generate OpenAPI Specification
```python
from scripts.openapi_generator import OpenAPIGenerator

generator = OpenAPIGenerator()
spec = generator.generate_spec(
    source_code=api_code,
    framework="fastapi",
    include_examples=True
)
print(f"OpenAPI version: {spec['openapi']}")
print(f"Endpoints: {len(spec['paths'])}")
```

### Create Postman Collection
```python
from scripts.postman_generator import PostmanGenerator

generator = PostmanGenerator()
collection = generator.create_collection(
    endpoints=endpoints,
    auth_schemes=["bearer", "api_key"]
)
print(f"Collection: {collection['info']['name']}")
print(f"Requests: {len(collection['item'])}")
```

### Generate Markdown Documentation
```python
from scripts.markdown_generator import MarkdownGenerator

generator = MarkdownGenerator()
markdown = generator.generate_docs(
    endpoints=endpoints,
    include_examples=True
)
print(f"Documentation generated: {len(markdown)} characters")
```

### Analyze API Code
```python
from scripts.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
analysis = analyzer.analyze_code(
    source_code=api_code,
    framework="fastapi"
)
print(f"Endpoints found: {analysis['endpoint_count']}")
print(f"Schemas detected: {analysis['schema_count']}")
```

## Output Format

All modules return structured JSON:

```json
{
  "documentation_type": "string",
  "format": "openapi|markdown|postman|html",
  "endpoints_documented": number,
  "schemas_generated": number,
  "examples_included": boolean,
  "authentication": ["array"],
  "openapi_spec": "object",
  "postman_collection": "object",
  "markdown_content": "string",
  "validation_status": "valid|warning|error",
  "recommendations": ["array of actionable items"]
}
```

## Severity Levels

| Level | Meaning | Impact | Action |
|-------|---------|--------|--------|
| CRITICAL | Missing authentication documentation | High risk | Document immediately |
| HIGH | Incomplete endpoint documentation | Moderate risk | Complete within sprint |
| MEDIUM | Missing request/response examples | Low-moderate risk | Add examples |
| LOW | Minor formatting inconsistency | Low risk | Consider for future |

## Version & Support

- **Version**: 1.0.0
- **Released**: February 2026
- **Status**: Production Ready
- **Confidence**: 93%

## Future Enhancements (v1.1.0)

- GraphQL schema documentation
- WebSocket endpoint documentation
- gRPC service documentation
- Automated changelog generation
- Multi-version API documentation
- Interactive API playground generation
- SDK code generation
- API diff comparison between versions
- Automated testing from documentation
- Integration with API management platforms

---
