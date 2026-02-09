"""
Postman Generator - Creates Postman collection from API endpoints
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class PostmanGenerator:
    """Generates Postman Collection v2.1 format"""
    
    def __init__(self):
        self.collection_version = "2.1.0"
    
    def create_collection(
        self,
        endpoints: List[Dict[str, Any]],
        collection_name: str = "API Collection",
        base_url: str = "{{base_url}}",
        auth_schemes: List[str] = None,
        include_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Create Postman collection from endpoints
        
        Args:
            endpoints: List of endpoint metadata
            collection_name: Name of the collection
            base_url: Base URL (can use Postman variables)
            auth_schemes: Authentication schemes to configure
            include_examples: Include response examples
            
        Returns:
            Postman collection in v2.1 format
        """
        auth_schemes = auth_schemes or []
        
        collection = {
            "info": self._generate_info(collection_name),
            "item": self._generate_items(endpoints, base_url, include_examples),
            "variable": self._generate_variables(base_url, auth_schemes)
        }
        
        # Add authentication if specified
        if auth_schemes:
            collection["auth"] = self._generate_auth(auth_schemes[0])
        
        return collection
    
    def _generate_info(self, collection_name: str) -> Dict[str, Any]:
        """Generate collection info"""
        return {
            "name": collection_name,
            "_postman_id": self._generate_id(),
            "description": "Auto-generated API collection",
            "schema": f"https://schema.getpostman.com/json/collection/v{self.collection_version}/collection.json"
        }
    
    def _generate_items(
        self,
        endpoints: List[Dict[str, Any]],
        base_url: str,
        include_examples: bool
    ) -> List[Dict[str, Any]]:
        """Generate collection items (requests)"""
        items = []
        
        # Group by tags if available
        grouped = self._group_by_tags(endpoints)
        
        for tag, tag_endpoints in grouped.items():
            if tag:
                # Create folder for tag
                folder = {
                    "name": tag,
                    "item": []
                }
                for endpoint in tag_endpoints:
                    folder["item"].append(self._generate_request(endpoint, base_url, include_examples))
                items.append(folder)
            else:
                # Add requests directly
                for endpoint in tag_endpoints:
                    items.append(self._generate_request(endpoint, base_url, include_examples))
        
        return items
    
    def _generate_request(
        self,
        endpoint: Dict[str, Any],
        base_url: str,
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate Postman request item"""
        request_name = endpoint.get("description", f"{endpoint['method']} {endpoint['path']}")
        
        item = {
            "name": request_name,
            "request": {
                "method": endpoint["method"],
                "url": self._generate_url(endpoint, base_url),
                "header": self._generate_headers(endpoint)
            }
        }
        
        # Add description
        if endpoint.get("description"):
            item["request"]["description"] = endpoint["description"]
        
        # Add request body for POST/PUT/PATCH
        if endpoint["method"] in ["POST", "PUT", "PATCH"]:
            item["request"]["body"] = self._generate_body(endpoint, include_examples)
        
        # Add response examples
        if include_examples:
            item["response"] = self._generate_responses(endpoint)
        
        return item
    
    def _generate_url(self, endpoint: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Generate URL object"""
        path = endpoint["path"]
        
        # Split path into segments
        segments = [s for s in path.split("/") if s]
        
        # Build path with variables
        path_vars = []
        for i, segment in enumerate(segments):
            if segment.startswith("{") and segment.endswith("}"):
                var_name = segment[1:-1]
                segments[i] = f":{var_name}"
                path_vars.append({
                    "key": var_name,
                    "value": "",
                    "description": f"Path parameter: {var_name}"
                })
        
        url = {
            "raw": f"{base_url}/{'/'.join(segments)}",
            "host": [base_url],
            "path": segments
        }
        
        # Add path variables
        if path_vars:
            url["variable"] = path_vars
        
        # Add query parameters
        query_params = [p for p in endpoint.get("parameters", []) if p["location"] == "query"]
        if query_params:
            url["query"] = [
                {
                    "key": p["name"],
                    "value": "",
                    "description": p.get("description", ""),
                    "disabled": not p.get("required", False)
                }
                for p in query_params
            ]
        
        return url
    
    def _generate_headers(self, endpoint: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate request headers"""
        headers = [
            {
                "key": "Content-Type",
                "value": "application/json",
                "type": "text"
            }
        ]
        
        # Add authentication header if specified
        if endpoint.get("authentication"):
            if endpoint["authentication"] in ["bearer", "bearerAuth"]:
                headers.append({
                    "key": "Authorization",
                    "value": "Bearer {{api_token}}",
                    "type": "text"
                })
            elif endpoint["authentication"] in ["api_key", "apiKeyAuth"]:
                headers.append({
                    "key": "X-API-Key",
                    "value": "{{api_key}}",
                    "type": "text"
                })
        
        # Add header parameters
        header_params = [p for p in endpoint.get("parameters", []) if p["location"] == "header"]
        for param in header_params:
            headers.append({
                "key": param["name"],
                "value": "",
                "type": "text",
                "description": param.get("description", "")
            })
        
        return headers
    
    def _generate_body(self, endpoint: Dict[str, Any], include_examples: bool) -> Dict[str, Any]:
        """Generate request body"""
        body = {
            "mode": "raw",
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }
        
        if include_examples:
            # Generate example body based on response model
            example = self._generate_example_body(endpoint.get("response_model"))
            body["raw"] = json.dumps(example, indent=2)
        else:
            body["raw"] = "{}"
        
        return body
    
    def _generate_responses(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate response examples"""
        responses = []
        
        # Success response
        responses.append({
            "name": "Success",
            "originalRequest": {},
            "status": "OK",
            "code": 200,
            "_postman_previewlanguage": "json",
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json"
                }
            ],
            "body": json.dumps(
                self._generate_example_body(endpoint.get("response_model")),
                indent=2
            )
        })
        
        return responses
    
    def _generate_auth(self, auth_scheme: str) -> Dict[str, Any]:
        """Generate authentication configuration"""
        if auth_scheme in ["bearer", "bearerAuth"]:
            return {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{api_token}}",
                        "type": "string"
                    }
                ]
            }
        elif auth_scheme in ["api_key", "apiKeyAuth"]:
            return {
                "type": "apikey",
                "apikey": [
                    {
                        "key": "key",
                        "value": "{{api_key}}",
                        "type": "string"
                    },
                    {
                        "key": "in",
                        "value": "header",
                        "type": "string"
                    }
                ]
            }
        return {}
    
    def _generate_variables(self, base_url: str, auth_schemes: List[str]) -> List[Dict[str, str]]:
        """Generate collection variables"""
        variables = [
            {
                "key": "base_url",
                "value": "https://api.example.com",
                "type": "string"
            }
        ]
        
        if "bearer" in auth_schemes or "bearerAuth" in auth_schemes:
            variables.append({
                "key": "api_token",
                "value": "",
                "type": "string"
            })
        
        if "api_key" in auth_schemes or "apiKeyAuth" in auth_schemes:
            variables.append({
                "key": "api_key",
                "value": "",
                "type": "string"
            })
        
        return variables
    
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
    
    def _generate_example_body(self, model_name: Optional[str]) -> Dict[str, Any]:
        """Generate example request/response body"""
        if model_name == "User":
            return {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2026-02-09T10:30:00Z"
            }
        return {}
    
    def _generate_id(self) -> str:
        """Generate unique Postman ID"""
        import uuid
        return str(uuid.uuid4())
    
    def export_collection(self, collection: Dict[str, Any], output_path: str) -> None:
        """Export collection to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(collection, f, indent=2)
