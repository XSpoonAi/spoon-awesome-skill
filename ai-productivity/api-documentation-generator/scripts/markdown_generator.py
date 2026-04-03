"""
Markdown Generator - Creates comprehensive markdown documentation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class MarkdownGenerator:
    """Generates markdown API documentation"""
    
    def __init__(self):
        self.sections = []
    
    def generate_docs(
        self,
        endpoints: List[Dict[str, Any]],
        api_info: Dict[str, str] = None,
        auth_schemes: List[str] = None,
        include_examples: bool = True
    ) -> str:
        """
        Generate comprehensive markdown documentation
        
        Args:
            endpoints: List of endpoint metadata
            api_info: API information (title, version, description)
            auth_schemes: Authentication schemes used
            include_examples: Include request/response examples
            
        Returns:
            Complete markdown documentation string
        """
        api_info = api_info or {}
        auth_schemes = auth_schemes or []
        
        self.sections = []
        
        # Generate sections
        self._add_header(api_info)
        self._add_toc(endpoints)
        self._add_getting_started(api_info)
        self._add_authentication(auth_schemes)
        self._add_endpoints(endpoints, include_examples)
        self._add_schemas(endpoints)
        self._add_error_codes()
        
        return "\n\n".join(self.sections)
    
    def _add_header(self, api_info: Dict[str, str]) -> None:
        """Add header section"""
        title = api_info.get("title", "API Documentation")
        version = api_info.get("version", "1.0.0")
        description = api_info.get("description", "")
        
        header = f"# {title}\n\n"
        header += f"**Version:** {version}\n\n"
        if description:
            header += f"{description}\n\n"
        header += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}"
        
        self.sections.append(header)
    
    def _add_toc(self, endpoints: List[Dict[str, Any]]) -> None:
        """Add table of contents"""
        toc = "## Table of Contents\n\n"
        toc += "- [Getting Started](#getting-started)\n"
        toc += "- [Authentication](#authentication)\n"
        toc += "- [Endpoints](#endpoints)\n"
        
        # Group by tags
        grouped = self._group_by_tags(endpoints)
        for tag in sorted(grouped.keys()):
            if tag:
                toc += f"  - [{tag}](#{tag.lower().replace(' ', '-')})\n"
        
        toc += "- [Schemas](#schemas)\n"
        toc += "- [Error Codes](#error-codes)"
        
        self.sections.append(toc)
    
    def _add_getting_started(self, api_info: Dict[str, str]) -> None:
        """Add getting started section"""
        section = "## Getting Started\n\n"
        
        base_url = api_info.get("base_url", "https://api.example.com")
        section += f"**Base URL:** `{base_url}`\n\n"
        
        section += "### Quick Example\n\n"
        section += "```bash\n"
        section += f"curl -X GET \"{base_url}/users\" \\\n"
        section += "  -H \"Authorization: Bearer YOUR_TOKEN\" \\\n"
        section += "  -H \"Content-Type: application/json\"\n"
        section += "```"
        
        self.sections.append(section)
    
    def _add_authentication(self, auth_schemes: List[str]) -> None:
        """Add authentication section"""
        section = "## Authentication\n\n"
        
        if not auth_schemes:
            section += "No authentication required."
            self.sections.append(section)
            return
        
        if "bearer" in auth_schemes or "bearerAuth" in auth_schemes:
            section += "### Bearer Token\n\n"
            section += "Include your API token in the Authorization header:\n\n"
            section += "```\n"
            section += "Authorization: Bearer YOUR_TOKEN\n"
            section += "```\n\n"
            section += "**Example:**\n\n"
            section += "```bash\n"
            section += "curl -H \"Authorization: Bearer eyJhbGci...\" https://api.example.com/users\n"
            section += "```\n\n"
        
        if "api_key" in auth_schemes or "apiKeyAuth" in auth_schemes:
            section += "### API Key\n\n"
            section += "Include your API key in the header:\n\n"
            section += "```\n"
            section += "X-API-Key: YOUR_API_KEY\n"
            section += "```\n\n"
            section += "**Example:**\n\n"
            section += "```bash\n"
            section += "curl -H \"X-API-Key: sk_live_abc123...\" https://api.example.com/users\n"
            section += "```\n\n"
        
        if "oauth2" in auth_schemes:
            section += "### OAuth 2.0\n\n"
            section += "This API uses OAuth 2.0 for authentication. Follow these steps:\n\n"
            section += "1. Redirect user to authorization URL\n"
            section += "2. User grants permission\n"
            section += "3. Exchange authorization code for access token\n"
            section += "4. Use access token in API requests\n\n"
        
        self.sections.append(section)
    
    def _add_endpoints(self, endpoints: List[Dict[str, Any]], include_examples: bool) -> None:
        """Add endpoints section"""
        section = "## Endpoints\n\n"
        
        # Group by tags
        grouped = self._group_by_tags(endpoints)
        
        for tag, tag_endpoints in sorted(grouped.items()):
            if tag:
                section += f"### {tag}\n\n"
            
            for endpoint in tag_endpoints:
                section += self._format_endpoint(endpoint, include_examples)
                section += "\n\n---\n\n"
        
        self.sections.append(section.rstrip("\n---\n\n"))
    
    def _format_endpoint(self, endpoint: Dict[str, Any], include_examples: bool) -> str:
        """Format a single endpoint"""
        method = endpoint["method"]
        path = endpoint["path"]
        description = endpoint.get("description", "")
        
        doc = f"#### `{method} {path}`\n\n"
        
        if description:
            doc += f"{description}\n\n"
        
        # Parameters
        parameters = endpoint.get("parameters", [])
        if parameters:
            doc += "**Parameters:**\n\n"
            doc += "| Name | Type | Location | Required | Description |\n"
            doc += "|------|------|----------|----------|-------------|\n"
            for param in parameters:
                required = "✓" if param.get("required") else "✗"
                desc = param.get("description", "-")
                doc += f"| `{param['name']}` | {param['type']} | {param['location']} | {required} | {desc} |\n"
            doc += "\n"
        
        # Request body
        if method in ["POST", "PUT", "PATCH"]:
            doc += "**Request Body:**\n\n"
            doc += "```json\n"
            doc += self._generate_example_json(endpoint.get("response_model"))
            doc += "\n```\n\n"
        
        # Response
        if include_examples:
            doc += "**Response:**\n\n"
            doc += "```json\n"
            doc += self._generate_example_json(endpoint.get("response_model"))
            doc += "\n```\n\n"
        
        # cURL example
        if include_examples:
            doc += "**Example Request:**\n\n"
            doc += "```bash\n"
            doc += self._generate_curl_example(endpoint)
            doc += "\n```\n\n"
        
        return doc
    
    def _add_schemas(self, endpoints: List[Dict[str, Any]]) -> None:
        """Add schemas section"""
        section = "## Schemas\n\n"
        
        # Extract unique schema names
        schemas = set()
        for endpoint in endpoints:
            if endpoint.get("response_model"):
                schemas.add(endpoint["response_model"])
        
        if not schemas:
            return
        
        for schema_name in sorted(schemas):
            section += f"### {schema_name}\n\n"
            section += "```json\n"
            section += self._generate_schema_definition(schema_name)
            section += "\n```\n\n"
        
        self.sections.append(section)
    
    def _add_error_codes(self) -> None:
        """Add error codes section"""
        section = "## Error Codes\n\n"
        section += "| Code | Status | Description |\n"
        section += "|------|--------|-------------|\n"
        section += "| 200 | OK | Request successful |\n"
        section += "| 201 | Created | Resource created successfully |\n"
        section += "| 400 | Bad Request | Invalid request parameters |\n"
        section += "| 401 | Unauthorized | Authentication required |\n"
        section += "| 403 | Forbidden | Insufficient permissions |\n"
        section += "| 404 | Not Found | Resource not found |\n"
        section += "| 429 | Too Many Requests | Rate limit exceeded |\n"
        section += "| 500 | Internal Server Error | Server error occurred |\n\n"
        
        section += "**Error Response Format:**\n\n"
        section += "```json\n"
        section += "{\n"
        section += '  "error": {\n'
        section += '    "code": "INVALID_REQUEST",\n'
        section += '    "message": "Detailed error message",\n'
        section += '    "details": {}\n'
        section += "  }\n"
        section += "}\n"
        section += "```"
        
        self.sections.append(section)
    
    def _group_by_tags(self, endpoints: List[Dict[str, Any]]) -> Dict[Optional[str], List[Dict[str, Any]]]:
        """Group endpoints by tags"""
        grouped = {}
        
        for endpoint in endpoints:
            tags = endpoint.get("tags", [None])
            tag = tags[0] if tags else None
            
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(endpoint)
        
        return grouped
    
    def _generate_example_json(self, model_name: Optional[str]) -> str:
        """Generate example JSON"""
        import json
        
        if model_name == "User":
            example = {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2026-02-09T10:30:00Z"
            }
        else:
            example = {}
        
        return json.dumps(example, indent=2)
    
    def _generate_schema_definition(self, schema_name: str) -> str:
        """Generate schema definition"""
        import json
        
        if schema_name == "User":
            schema = {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "User ID"},
                    "name": {"type": "string", "description": "User's full name"},
                    "email": {"type": "string", "format": "email", "description": "User's email address"},
                    "created_at": {"type": "string", "format": "date-time", "description": "Account creation timestamp"}
                },
                "required": ["id", "name", "email"]
            }
        else:
            schema = {"type": "object"}
        
        return json.dumps(schema, indent=2)
    
    def _generate_curl_example(self, endpoint: Dict[str, Any]) -> str:
        """Generate cURL command example"""
        method = endpoint["method"]
        path = endpoint["path"]
        
        # Replace path parameters
        example_path = path
        for param in endpoint.get("parameters", []):
            if param["location"] == "path":
                example_path = example_path.replace(f"{{{param['name']}}}", "123")
        
        curl = f"curl -X {method} \"https://api.example.com{example_path}\""
        
        # Add authentication header
        if endpoint.get("authentication"):
            curl += " \\\n  -H \"Authorization: Bearer YOUR_TOKEN\""
        
        curl += " \\\n  -H \"Content-Type: application/json\""
        
        # Add request body
        if method in ["POST", "PUT", "PATCH"]:
            curl += " \\\n  -d '" + self._generate_example_json(endpoint.get("response_model")) + "'"
        
        return curl
    
    def save_to_file(self, content: str, output_path: str) -> None:
        """Save markdown to file"""
        with open(output_path, 'w') as f:
            f.write(content)
