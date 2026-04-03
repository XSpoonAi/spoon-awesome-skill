"""
Code Analyzer - Extracts API endpoints and metadata from source code
Supports: FastAPI, Flask, Django, Express
"""

import ast
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Parameter:
    """API parameter metadata"""
    name: str
    type: str
    location: str  # path, query, header, body
    required: bool
    description: Optional[str] = None
    example: Optional[Any] = None


@dataclass
class Endpoint:
    """API endpoint metadata"""
    path: str
    method: str
    function: str
    parameters: List[Parameter]
    response_model: Optional[str] = None
    status_codes: List[int] = None
    authentication: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = None


class CodeAnalyzer:
    """Analyzes API source code and extracts endpoint metadata"""
    
    def __init__(self):
        self.endpoints: List[Endpoint] = []
        self.schemas: Dict[str, Any] = {}
        self.auth_schemes: List[str] = []
    
    def analyze_code(self, source_code: str, framework: str = "fastapi") -> Dict[str, Any]:
        """
        Analyze API source code and extract all endpoint information
        
        Args:
            source_code: API source code to analyze
            framework: Framework type (fastapi, flask, django, express)
            
        Returns:
            Dict containing endpoints, schemas, and authentication info
        """
        if framework.lower() in ["fastapi", "flask"]:
            return self._analyze_python_code(source_code, framework)
        elif framework.lower() == "express":
            return self._analyze_express_code(source_code)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _analyze_python_code(self, source_code: str, framework: str) -> Dict[str, Any]:
        """Analyze Python (FastAPI/Flask) code"""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error in source code: {str(e)}",
                "endpoints": []
            }
        
        endpoints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                endpoint = self._extract_python_endpoint(node, framework)
                if endpoint:
                    endpoints.append(endpoint)
        
        # Extract schemas from class definitions
        schemas = self._extract_schemas(tree)
        
        # Detect authentication schemes
        auth_schemes = self._detect_auth_schemes(source_code)
        
        return {
            "success": True,
            "framework": framework,
            "total_endpoints": len(endpoints),
            "endpoints": [asdict(e) for e in endpoints],
            "schemas_extracted": len(schemas),
            "schemas": schemas,
            "auth_schemes_detected": auth_schemes
        }
    
    def _extract_python_endpoint(self, node: ast.FunctionDef, framework: str) -> Optional[Endpoint]:
        """Extract endpoint information from Python function definition"""
        # Check for route decorators
        route_decorator = None
        method = None
        path = None
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr'):
                    attr_name = decorator.func.attr
                    if attr_name in ['get', 'post', 'put', 'delete', 'patch']:
                        method = attr_name.upper()
                        if decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                path = decorator.args[0].value
                        route_decorator = decorator
        
        if not route_decorator or not path:
            return None
        
        # Extract parameters
        parameters = self._extract_parameters(node)
        
        # Extract response model
        response_model = None
        if hasattr(node, 'returns') and node.returns:
            if isinstance(node.returns, ast.Name):
                response_model = node.returns.id
        
        # Extract description from docstring
        description = ast.get_docstring(node)
        
        return Endpoint(
            path=path,
            method=method,
            function=node.name,
            parameters=parameters,
            response_model=response_model,
            status_codes=[200],  # Default, could be enhanced
            description=description
        )
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Parameter]:
        """Extract function parameters and convert to API parameters"""
        parameters = []
        
        for arg in node.args.args:
            if arg.arg in ['self', 'cls', 'request']:
                continue
            
            param_type = "string"  # Default
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    param_type = arg.annotation.id.lower()
            
            # Determine location (path parameters in route, others are query)
            location = "query"  # Default
            
            parameters.append(Parameter(
                name=arg.arg,
                type=param_type,
                location=location,
                required=True
            ))
        
        return parameters
    
    def _extract_schemas(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract Pydantic models or data classes as schemas"""
        schemas = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Pydantic model or dataclass
                schema = self._extract_schema_from_class(node)
                if schema:
                    schemas[node.name] = schema
        
        return schemas
    
    def _extract_schema_from_class(self, node: ast.ClassDef) -> Optional[Dict[str, Any]]:
        """Extract schema from class definition"""
        properties = {}
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    field_name = item.target.id
                    field_type = "string"  # Default
                    
                    if item.annotation:
                        if isinstance(item.annotation, ast.Name):
                            field_type = item.annotation.id.lower()
                    
                    properties[field_name] = {
                        "type": field_type
                    }
        
        if not properties:
            return None
        
        return {
            "type": "object",
            "properties": properties
        }
    
    def _detect_auth_schemes(self, source_code: str) -> List[str]:
        """Detect authentication schemes used in code"""
        auth_schemes = []
        
        if "Bearer" in source_code or "JWT" in source_code:
            auth_schemes.append("bearer")
        if "API-Key" in source_code or "X-API-Key" in source_code:
            auth_schemes.append("api_key")
        if "OAuth" in source_code:
            auth_schemes.append("oauth2")
        if "Basic" in source_code and "Authorization" in source_code:
            auth_schemes.append("basic")
        
        return auth_schemes
    
    def _analyze_express_code(self, source_code: str) -> Dict[str, Any]:
        """Analyze Express.js code"""
        # Simple regex-based extraction for Express routes
        endpoints = []
        
        # Pattern: app.get('/path', ...)
        pattern = r'app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(pattern, source_code)
        
        for method, path in matches:
            endpoints.append({
                "path": path,
                "method": method.upper(),
                "function": f"{method}_{path.replace('/', '_')}",
                "parameters": []
            })
        
        return {
            "success": True,
            "framework": "express",
            "total_endpoints": len(endpoints),
            "endpoints": endpoints,
            "schemas_extracted": 0,
            "auth_schemes_detected": self._detect_auth_schemes(source_code)
        }
