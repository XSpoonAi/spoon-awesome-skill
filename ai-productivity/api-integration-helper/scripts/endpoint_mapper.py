#!/usr/bin/env python3
"""
API Endpoint Mapper
Discovers, analyzes, and catalogs API endpoints
"""

import re
from typing import Dict, List, Any
from collections import defaultdict

class EndpointMapper:
    """Maps and analyzes API endpoints from code and OpenAPI specs."""

    def __init__(self):
        self.http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        self.frameworks = {
            "flask": {
                "decorator": "@app.route",
                "method_param": "methods"
            },
            "fastapi": {
                "decorator": "@app.",
                "method_param": "methods"
            },
            "django": {
                "pattern": "path\\(",
                "method_in_view": True
            },
            "express": {
                "decorator": "app\\.",
                "method_param": "direct"
            }
        }

    def map_from_code(self, code: str, framework: str = "flask") -> Dict[str, Any]:
        """Extract API endpoints from source code."""
        
        endpoints = []
        
        if framework == "flask":
            endpoints = self._extract_flask_endpoints(code)
        elif framework == "fastapi":
            endpoints = self._extract_fastapi_endpoints(code)
        elif framework == "django":
            endpoints = self._extract_django_endpoints(code)
        elif framework == "express":
            endpoints = self._extract_express_endpoints(code)
        
        return {
            "framework": framework,
            "total_endpoints": len(endpoints),
            "endpoints": self._analyze_endpoints(endpoints),
            "recommendations": self._get_recommendations(endpoints)
        }

    def map_from_openapi(self, spec: Dict) -> Dict[str, Any]:
        """Extract endpoints from OpenAPI specification."""
        
        endpoints = []
        paths = spec.get("paths", {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in self.http_methods:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "operation_id": details.get("operationId", ""),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "tags": details.get("tags", []),
                        "parameters": len(details.get("parameters", [])),
                        "required_params": self._count_required_params(details.get("parameters", [])),
                        "authentication": details.get("security", [])
                    }
                    endpoints.append(endpoint)
        
        return {
            "api_version": spec.get("info", {}).get("version", "unknown"),
            "api_title": spec.get("info", {}).get("title", "Unknown API"),
            "total_endpoints": len(endpoints),
            "endpoints": endpoints,
            "coverage_analysis": self._analyze_coverage(endpoints),
            "security_analysis": self._analyze_security(spec)
        }

    def categorize_endpoints(self, endpoints: List[Dict]) -> Dict[str, List]:
        """Organize endpoints by resource and method."""
        
        categories = defaultdict(lambda: defaultdict(list))
        
        for endpoint in endpoints:
            path = endpoint.get("path", "")
            method = endpoint.get("method", "GET")
            
            # Extract resource from path
            resource = self._extract_resource(path)
            categories[resource][method].append(endpoint)
        
        result = {}
        for resource, methods in categories.items():
            result[resource] = dict(methods)
        
        return result

    def generate_client_code(self, endpoints: List[Dict], language: str = "python") -> Dict[str, str]:
        """Generate API client code for endpoints."""
        
        client_code = {}
        
        if language == "python":
            client_code["client"] = self._generate_python_client(endpoints)
        elif language == "javascript":
            client_code["client"] = self._generate_js_client(endpoints)
        elif language == "typescript":
            client_code["client"] = self._generate_ts_client(endpoints)
        
        return client_code

    def analyze_endpoint_patterns(self, endpoints: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns and consistency in endpoint design."""
        
        paths = [e.get("path", "") for e in endpoints]
        methods_dist = defaultdict(int)
        
        for e in endpoints:
            methods_dist[e.get("method", "GET")] += 1
        
        issues = []
        recommendations = []
        
        # Check for inconsistent naming
        resource_patterns = self._extract_resource_patterns(paths)
        if len(resource_patterns) > 2:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Inconsistent naming conventions",
                "resources": list(resource_patterns.keys())
            })
            recommendations.append("Use consistent plural/singular for resources")
        
        # Check for deep nesting
        deep_paths = [p for p in paths if p.count("/") > 4]
        if deep_paths:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Deep path nesting detected",
                "count": len(deep_paths),
                "examples": deep_paths[:3]
            })
            recommendations.append("Consider flattening URL structure")
        
        # Check method distribution
        if "GET" not in methods_dist:
            issues.append({
                "severity": "LOW",
                "issue": "No GET endpoints found",
                "recommendation": "APIs typically have read operations"
            })
        
        return {
            "total_endpoints": len(endpoints),
            "method_distribution": dict(methods_dist),
            "unique_resources": len(resource_patterns),
            "max_nesting_level": max([p.count("/") for p in paths] or [0]),
            "issues": issues,
            "recommendations": recommendations,
            "design_score": max(0, 100 - len(issues) * 15)
        }

    def detect_versioning(self, endpoints: List[Dict]) -> Dict[str, Any]:
        """Detect API versioning strategy."""
        
        paths = [e.get("path", "") for e in endpoints]
        
        url_version = any(re.search(r"/v\d+", p) for p in paths)
        header_version = False  # Would need headers analysis
        accept_version = False  # Would need content-type analysis
        
        strategy = "unknown"
        if url_version:
            versions = re.findall(r"/v(\d+)", " ".join(paths))
            strategy = f"URL path versioning (versions: {', '.join(set(versions))})"
        elif header_version:
            strategy = "Header-based versioning"
        elif accept_version:
            strategy = "Content negotiation versioning"
        else:
            strategy = "No versioning detected"
        
        return {
            "versioning_strategy": strategy,
            "recommendations": [
                "Use semantic versioning (v1, v2, v3)",
                "Deprecate old versions after 12-18 months",
                "Provide migration guide for version upgrades"
            ] if strategy == "No versioning detected" else []
        }

    # ===== Private Methods =====

    def _extract_flask_endpoints(self, code: str) -> List[Dict]:
        """Extract Flask route endpoints."""
        endpoints = []
        
        # Match @app.route() and @app.post(), @app.get(), etc.
        route_pattern = r"@app\.route\(['\"]([^'\"]+)['\"]\s*(?:,\s*methods\s*=\s*\[([^\]]+)\])?\)"
        method_pattern = r"@app\.(\w+)\(['\"]([^'\"]+)['\"]\)"
        
        for match in re.finditer(route_pattern, code):
            path = match.group(1)
            methods = match.group(2) or "GET"
            methods = [m.strip().strip("'\"") for m in methods.split(",")]
            
            for method in methods:
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "framework": "flask"
                })
        
        for match in re.finditer(method_pattern, code):
            method = match.group(1).upper()
            path = match.group(2)
            
            if method in self.http_methods:
                endpoints.append({
                    "path": path,
                    "method": method,
                    "framework": "flask"
                })
        
        return endpoints

    def _extract_fastapi_endpoints(self, code: str) -> List[Dict]:
        """Extract FastAPI route endpoints."""
        endpoints = []
        
        # Match @app.get(), @app.post(), etc.
        pattern = r"@app\.(\w+)\(['\"]([^'\"]+)['\"]\)"
        
        for match in re.finditer(pattern, code):
            method = match.group(1).upper()
            path = match.group(2)
            
            if method in self.http_methods or method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                endpoints.append({
                    "path": path,
                    "method": method if method in self.http_methods else "GET",
                    "framework": "fastapi"
                })
        
        return endpoints

    def _extract_django_endpoints(self, code: str) -> List[Dict]:
        """Extract Django URL endpoints."""
        endpoints = []
        
        # Match path() and re_path()
        pattern = r"path\(['\"]([^'\"]+)['\"],\s*(\w+\.[\w\.]+)\)"
        
        for match in re.finditer(pattern, code):
            path = match.group(1)
            endpoints.append({
                "path": path,
                "method": "GET,POST",  # Django views handle multiple methods
                "framework": "django"
            })
        
        return endpoints

    def _extract_express_endpoints(self, code: str) -> List[Dict]:
        """Extract Express.js route endpoints."""
        endpoints = []
        
        # Match app.get(), app.post(), etc.
        pattern = r"app\.(\w+)\(['\"]([^'\"]+)['\"]\)"
        
        for match in re.finditer(pattern, code):
            method = match.group(1).upper()
            path = match.group(2)
            
            if method in self.http_methods:
                endpoints.append({
                    "path": path,
                    "method": method,
                    "framework": "express"
                })
        
        return endpoints

    def _analyze_endpoints(self, endpoints: List[Dict]) -> List[Dict]:
        """Analyze and enrich endpoint information."""
        analyzed = []
        
        for ep in endpoints:
            analyzed.append({
                **ep,
                "resource": self._extract_resource(ep.get("path", "")),
                "path_parameters": self._count_path_params(ep.get("path", "")),
                "complexity": self._calculate_complexity(ep.get("path", ""))
            })
        
        return analyzed

    def _extract_resource(self, path: str) -> str:
        """Extract main resource from path."""
        parts = [p for p in path.split("/") if p and not p.startswith("{") and not p.startswith(":")]
        return parts[0] if parts else "root"

    def _extract_resource_patterns(self, paths: List[str]) -> Dict:
        """Extract resource patterns from paths."""
        patterns = defaultdict(int)
        
        for path in paths:
            parts = [p for p in path.split("/") if p]
            if parts:
                resource = parts[0]
                # Check if plural or singular
                if resource.endswith("s"):
                    patterns[f"{resource} (plural)"] += 1
                else:
                    patterns[f"{resource} (singular)"] += 1
        
        return patterns

    def _count_path_params(self, path: str) -> int:
        """Count path parameters."""
        return len(re.findall(r"\{[^}]+\}|:[a-zA-Z_]\w*", path))

    def _calculate_complexity(self, path: str) -> str:
        """Calculate endpoint complexity."""
        nesting = path.count("/") - 1
        params = self._count_path_params(path)
        
        complexity = nesting + params
        if complexity <= 1:
            return "SIMPLE"
        elif complexity <= 3:
            return "MODERATE"
        else:
            return "COMPLEX"

    def _count_required_params(self, parameters: List[Dict]) -> int:
        """Count required parameters."""
        return sum(1 for p in parameters if p.get("required", False))

    def _analyze_coverage(self, endpoints: List[Dict]) -> Dict:
        """Analyze endpoint coverage and patterns."""
        resources = defaultdict(list)
        
        for ep in endpoints:
            resource = ep.get("path", "").split("/")[1] if "/" in ep.get("path", "") else "root"
            resources[resource].append(ep)
        
        return {
            "total_resources": len(resources),
            "endpoints_per_resource": {r: len(eps) for r, eps in resources.items()}
        }

    def _analyze_security(self, spec: Dict) -> Dict:
        """Analyze security schemes."""
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        global_security = spec.get("security", [])
        
        return {
            "security_schemes": list(security_schemes.keys()),
            "global_security_required": len(global_security) > 0,
            "total_schemes": len(security_schemes)
        }

    def _get_recommendations(self, endpoints: List[Dict]) -> List[str]:
        """Generate recommendations for endpoints."""
        recommendations = []
        
        if not endpoints:
            recommendations.append("No endpoints detected")
        
        methods = defaultdict(int)
        for ep in endpoints:
            methods[ep.get("method", "GET")] += 1
        
        if not methods.get("POST"):
            recommendations.append("Consider adding POST endpoints for data creation")
        
        if not methods.get("DELETE"):
            recommendations.append("Consider adding DELETE endpoints for data removal")
        
        return recommendations

    def _generate_python_client(self, endpoints: List[Dict]) -> str:
        """Generate Python API client."""
        code = '''import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
'''
        for ep in endpoints[:5]:  # First 5 endpoints
            method = ep.get("method", "GET").lower()
            path = ep.get("path", "/")
            func_name = self._path_to_function_name(path)
            
            code += f'''    def {func_name}(self, **kwargs) -> Dict[str, Any]:
        """Call {method.upper()} {path}"""
        url = f"{{self.base_url}}{path}"
        response = requests.{method}(url, **kwargs)
        return response.json()
    
'''
        
        return code

    def _generate_js_client(self, endpoints: List[Dict]) -> str:
        """Generate JavaScript API client."""
        code = '''class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }
'''
        for ep in endpoints[:5]:
            method = ep.get("method", "GET").lower()
            path = ep.get("path", "/")
            func_name = self._path_to_function_name(path)
            
            code += f'''
    async {func_name}(options = {{}}) {{
        const response = await fetch(`${{this.baseURL}}{path}`, {{
            method: '{method.upper()}',
            ...options
        }});
        return response.json();
    }}
'''
        code += '\n}\n'
        return code

    def _generate_ts_client(self, endpoints: List[Dict]) -> str:
        """Generate TypeScript API client."""
        code = '''import axios, { AxiosInstance } from 'axios';

class APIClient {
    private client: AxiosInstance;
    
    constructor(baseURL: string) {
        this.client = axios.create({ baseURL });
    }
'''
        for ep in endpoints[:5]:
            method = ep.get("method", "GET").lower()
            path = ep.get("path", "/")
            func_name = self._path_to_function_name(path)
            
            code += f'''
    async {func_name}(data?: any): Promise<any> {{
        return this.client.{method}('{path}', data);
    }}
'''
        code += '\n}\n'
        return code

    def _path_to_function_name(self, path: str) -> str:
        """Convert path to function name."""
        parts = path.split("/")
        parts = [p.replace("{", "").replace("}", "") for p in parts if p]
        return "_".join(parts) if parts else "root"


if __name__ == "__main__":
    mapper = EndpointMapper()
    
    # Test with Flask code
    flask_code = '''
@app.route('/users', methods=['GET'])
def list_users():
    return {"users": []}

@app.post('/users')
def create_user():
    return {"id": 1}

@app.get('/users/<id>')
def get_user(id):
    return {"id": id}
'''
    
    result = mapper.map_from_code(flask_code, "flask")
    import json
    print(json.dumps(result, indent=2))
