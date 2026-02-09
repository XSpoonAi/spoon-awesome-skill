"""
OpenAPI Generator - Generates OpenAPI 3.0 specifications from analyzed endpoints
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class OpenAPIGenerator:
    """Generates OpenAPI 3.0 specifications"""
    
    def __init__(self):
        self.spec_version = "3.0.3"
    
    def generate_spec(
        self,
        endpoints: List[Dict[str, Any]],
        schemas: Dict[str, Any] = None,
        auth_schemes: List[str] = None,
        api_info: Dict[str, str] = None,
        include_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete OpenAPI 3.0 specification
        
        Args:
            endpoints: List of endpoint metadata
            schemas: Dictionary of schema definitions
            auth_schemes: List of authentication schemes
            api_info: API metadata (title, version, description)
            include_examples: Include request/response examples
            
        Returns:
            Complete OpenAPI 3.0 specification
        """
        schemas = schemas or {}
        auth_schemes = auth_schemes or []
        api_info = api_info or {}
        
        spec = {
            "openapi": self.spec_version,
            "info": self._generate_info(api_info),
            "paths": self._generate_paths(endpoints, include_examples),
            "components": self._generate_components(schemas, auth_schemes)
        }
        
        # Add servers if provided
        if "servers" in api_info:
            spec["servers"] = api_info["servers"]
        else:
            spec["servers"] = [{"url": "https://api.example.com", "description": "Production server"}]
        
        # Add tags
        tags = self._extract_tags(endpoints)
        if tags:
            spec["tags"] = tags
        
        return spec
    
    def _generate_info(self, api_info: Dict[str, str]) -> Dict[str, Any]:
        """Generate API info section"""
        return {
            "title": api_info.get("title", "API Documentation"),
            "version": api_info.get("version", "1.0.0"),
            "description": api_info.get("description", "Auto-generated API documentation"),
            "contact": api_info.get("contact", {}),
            "license": api_info.get("license", {})
        }
    
    def _generate_paths(
        self,
        endpoints: List[Dict[str, Any]],
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate paths section"""
        paths = {}
        
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = self._generate_operation(endpoint, include_examples)
        
        return paths
    
    def _generate_operation(
        self,
        endpoint: Dict[str, Any],
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate operation object for an endpoint"""
        operation = {
            "summary": endpoint.get("description", f"{endpoint['method']} {endpoint['path']}"),
            "operationId": endpoint.get("function", f"{endpoint['method']}_{endpoint['path'].replace('/', '_')}"),
            "parameters": [],
            "responses": self._generate_responses(endpoint, include_examples)
        }
        
        # Add tags
        if endpoint.get("tags"):
            operation["tags"] = endpoint["tags"]
        
        # Add parameters
        for param in endpoint.get("parameters", []):
            operation["parameters"].append(self._generate_parameter(param, include_examples))
        
        # Add request body if POST/PUT/PATCH
        if endpoint["method"] in ["POST", "PUT", "PATCH"]:
            operation["requestBody"] = self._generate_request_body(endpoint, include_examples)
        
        # Add security
        if endpoint.get("authentication"):
            operation["security"] = [{endpoint["authentication"]: []}]
        
        return operation
    
    def _generate_parameter(
        self,
        param: Dict[str, Any],
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate parameter object"""
        parameter = {
            "name": param["name"],
            "in": param["location"],
            "required": param.get("required", False),
            "schema": {"type": self._map_type(param.get("type", "string"))}
        }
        
        if param.get("description"):
            parameter["description"] = param["description"]
        
        if include_examples and param.get("example"):
            parameter["example"] = param["example"]
        
        return parameter
    
    def _generate_request_body(
        self,
        endpoint: Dict[str, Any],
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate request body object"""
        request_body = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {}
                }
            }
        }
        
        # If response_model is specified, use it as schema reference
        if endpoint.get("response_model"):
            request_body["content"]["application/json"]["schema"] = {
                "$ref": f"#/components/schemas/{endpoint['response_model']}"
            }
        else:
            request_body["content"]["application/json"]["schema"] = {
                "type": "object"
            }
        
        if include_examples:
            request_body["content"]["application/json"]["example"] = self._generate_example(
                endpoint.get("response_model")
            )
        
        return request_body
    
    def _generate_responses(
        self,
        endpoint: Dict[str, Any],
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate responses object"""
        responses = {}
        
        # Success response
        status_codes = endpoint.get("status_codes", [200])
        for status_code in status_codes:
            if 200 <= status_code < 300:
                responses[str(status_code)] = {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {}
                        }
                    }
                }
                
                # Add schema reference if available
                if endpoint.get("response_model"):
                    responses[str(status_code)]["content"]["application/json"]["schema"] = {
                        "$ref": f"#/components/schemas/{endpoint['response_model']}"
                    }
                else:
                    responses[str(status_code)]["content"]["application/json"]["schema"] = {
                        "type": "object"
                    }
                
                if include_examples:
                    responses[str(status_code)]["content"]["application/json"]["example"] = \
                        self._generate_example(endpoint.get("response_model"))
        
        # Error responses
        responses["400"] = {"description": "Bad request"}
        responses["401"] = {"description": "Unauthorized"}
        responses["404"] = {"description": "Not found"}
        responses["500"] = {"description": "Internal server error"}
        
        return responses
    
    def _generate_components(
        self,
        schemas: Dict[str, Any],
        auth_schemes: List[str]
    ) -> Dict[str, Any]:
        """Generate components section"""
        components = {
            "schemas": schemas,
            "securitySchemes": {}
        }
        
        # Add security schemes
        for scheme in auth_schemes:
            if scheme == "bearer":
                components["securitySchemes"]["bearerAuth"] = {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            elif scheme == "api_key":
                components["securitySchemes"]["apiKeyAuth"] = {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            elif scheme == "oauth2":
                components["securitySchemes"]["oauth2"] = {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": "https://auth.example.com/oauth/authorize",
                            "tokenUrl": "https://auth.example.com/oauth/token",
                            "scopes": {}
                        }
                    }
                }
        
        return components
    
    def _extract_tags(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract unique tags from endpoints"""
        tags_set = set()
        for endpoint in endpoints:
            if endpoint.get("tags"):
                tags_set.update(endpoint["tags"])
        
        return [{"name": tag} for tag in sorted(tags_set)]
    
    def _map_type(self, type_str: str) -> str:
        """Map Python/programming types to OpenAPI types"""
        type_map = {
            "int": "integer",
            "float": "number",
            "str": "string",
            "bool": "boolean",
            "list": "array",
            "dict": "object"
        }
        return type_map.get(type_str.lower(), "string")
    
    def _generate_example(self, model_name: Optional[str]) -> Any:
        """Generate example data"""
        if model_name == "User":
            return {"id": 1, "name": "John Doe", "email": "john@example.com"}
        return {}
    
    def export_json(self, spec: Dict[str, Any], output_path: str) -> None:
        """Export specification to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(spec, f, indent=2)
    
    def export_yaml(self, spec: Dict[str, Any], output_path: str) -> None:
        """Export specification to YAML file"""
        try:
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(spec, f, default_flow_style=False)
        except ImportError:
            raise ImportError("PyYAML not installed. Run: pip install pyyaml")
