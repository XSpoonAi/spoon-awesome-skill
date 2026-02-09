#!/usr/bin/env python3
"""
API Authentication Handler
Manages and validates API authentication schemes
"""

import hashlib
import hmac
import json
import time
from typing import Dict, List, Any, Optional
from enum import Enum

class AuthType(Enum):
    """API authentication types."""
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    HMAC = "hmac"
    JWT = "jwt"
    CUSTOM = "custom"

class AuthHandler:
    """Handles API authentication configuration and validation."""

    def __init__(self):
        self.auth_types = {
            "basic": self._validate_basic_auth,
            "bearer": self._validate_bearer_auth,
            "api_key": self._validate_api_key_auth,
            "oauth2": self._validate_oauth2_auth,
            "hmac": self._validate_hmac_auth,
            "jwt": self._validate_jwt_auth
        }

    def detect_auth_scheme(self, headers: Dict, url: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """Detect authentication scheme from request details."""
        
        detected_schemes = []
        confidence_scores = {}
        
        # Check Authorization header
        auth_header = headers.get("Authorization", "")
        if auth_header:
            if auth_header.lower().startswith("basic "):
                detected_schemes.append("basic")
                confidence_scores["basic"] = 95
            elif auth_header.lower().startswith("bearer "):
                detected_schemes.append("bearer")
                confidence_scores["bearer"] = 95
            elif auth_header.lower().startswith("apikey "):
                detected_schemes.append("api_key")
                confidence_scores["api_key"] = 90
        
        # Check for API key in headers
        api_key_headers = ["X-API-Key", "x-api-key", "API-Key", "api-key"]
        for header in api_key_headers:
            if header in headers or header.lower() in {k.lower(): k for k in headers}:
                if "api_key" not in detected_schemes:
                    detected_schemes.append("api_key")
                    confidence_scores["api_key"] = 85
        
        # Check for OAuth tokens
        if "access_token" in headers:
            detected_schemes.append("oauth2")
            confidence_scores["oauth2"] = 80
        
        # Check for HMAC signature
        if "X-Signature" in headers or "X-HMAC-SHA256" in headers:
            detected_schemes.append("hmac")
            confidence_scores["hmac"] = 90
        
        # Check for JWT
        if auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ")[1] if " " in auth_header else ""
            if token.count(".") == 2:  # JWT format
                detected_schemes.append("jwt")
                if "bearer" in confidence_scores:
                    del confidence_scores["bearer"]
                confidence_scores["jwt"] = 92
        
        primary_scheme = detected_schemes[0] if detected_schemes else "unknown"
        
        return {
            "detected_schemes": detected_schemes,
            "primary_scheme": primary_scheme,
            "confidence_scores": confidence_scores,
            "recommendations": self._get_auth_recommendations(detected_schemes)
        }

    def validate_credentials(self, auth_type: str, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate authentication credentials."""
        
        if auth_type in self.auth_types:
            return self.auth_types[auth_type](credentials, config)
        
        return {
            "is_valid": False,
            "error": f"Unknown auth type: {auth_type}",
            "supported_types": list(self.auth_types.keys())
        }

    def generate_auth_header(self, auth_type: str, credentials: Dict) -> Dict[str, str]:
        """Generate authentication header."""
        
        headers = {}
        
        if auth_type == "basic":
            import base64
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            credentials_str = f"{username}:{password}"
            encoded = base64.b64encode(credentials_str.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        elif auth_type == "bearer":
            token = credentials.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == "api_key":
            key = credentials.get("key", "")
            location = credentials.get("location", "header")
            header_name = credentials.get("header_name", "X-API-Key")
            
            if location == "header":
                headers[header_name] = key
            elif location == "query":
                # Return with special marker for query param
                headers["__query_param__"] = f"{header_name}={key}"
        
        elif auth_type == "hmac":
            headers.update(self._generate_hmac_headers(credentials))
        
        elif auth_type == "oauth2":
            token = credentials.get("access_token", "")
            headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == "jwt":
            token = credentials.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        
        return headers

    def analyze_security_risks(self, auth_config: Dict) -> Dict[str, Any]:
        """Analyze security risks in authentication setup."""
        
        risks = []
        recommendations = []
        
        auth_type = auth_config.get("type", "unknown")
        
        # Basic Auth risks
        if auth_type == "basic":
            risks.append({
                "risk": "Credentials in every request",
                "severity": "HIGH",
                "mitigation": "Always use HTTPS with Basic Auth"
            })
            recommendations.append("Rotate credentials regularly")
            recommendations.append("Use HTTPS exclusively")
            recommendations.append("Consider Bearer tokens instead")
        
        # API Key risks
        elif auth_type == "api_key":
            if auth_config.get("location") == "query":
                risks.append({
                    "risk": "API key exposed in URL",
                    "severity": "CRITICAL",
                    "mitigation": "Move to HTTP headers"
                })
            
            if auth_config.get("key_length", 32) < 32:
                risks.append({
                    "risk": "Weak key length",
                    "severity": "MEDIUM",
                    "mitigation": "Use at least 256-bit keys"
                })
            
            recommendations.append("Implement key rotation policy")
            recommendations.append("Monitor key usage")
            recommendations.append("Revoke unused keys")
        
        # OAuth2 risks
        elif auth_type == "oauth2":
            flow = auth_config.get("flow", "unknown")
            
            if flow == "implicit":
                risks.append({
                    "risk": "Implicit flow is deprecated",
                    "severity": "HIGH",
                    "mitigation": "Use Authorization Code flow with PKCE"
                })
            
            if not auth_config.get("scopes"):
                risks.append({
                    "risk": "No scopes defined",
                    "severity": "MEDIUM",
                    "mitigation": "Define minimum required scopes"
                })
            
            recommendations.append("Use PKCE for public clients")
            recommendations.append("Implement refresh token rotation")
            recommendations.append("Set reasonable token expiration")
        
        # JWT risks
        elif auth_type == "jwt":
            if not auth_config.get("verification_key"):
                risks.append({
                    "risk": "No signature verification",
                    "severity": "CRITICAL",
                    "mitigation": "Verify JWT signature"
                })
            
            if auth_config.get("algorithm") == "none":
                risks.append({
                    "risk": "JWT with 'none' algorithm",
                    "severity": "CRITICAL",
                    "mitigation": "Use HS256 or RS256"
                })
            
            recommendations.append("Verify issuer and audience claims")
            recommendations.append("Check token expiration")
            recommendations.append("Monitor token usage")
        
        score = max(0, 100 - len(risks) * 25)
        
        return {
            "security_score": score,
            "risk_count": len(risks),
            "risks": risks,
            "recommendations": recommendations,
            "overall_assessment": "SECURE" if score > 80 else "MODERATE" if score > 60 else "INSECURE"
        }

    def generate_auth_documentation(self, auth_config: Dict) -> str:
        """Generate documentation for authentication."""
        
        auth_type = auth_config.get("type", "unknown")
        
        doc = f"# Authentication: {auth_type.upper()}\n\n"
        
        if auth_type == "basic":
            doc += """## Basic Authentication

### Format
\`\`\`
Authorization: Basic base64(username:password)
\`\`\`

### Example
\`\`\`bash
curl -H "Authorization: Basic dXNlcjpwYXNz" https://api.example.com/resource
\`\`\`

### Python
\`\`\`python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'https://api.example.com/resource',
    auth=HTTPBasicAuth('username', 'password')
)
\`\`\`

### Security
- ⚠️ Always use HTTPS
- ⚠️ Credentials are Base64 encoded (not encrypted)
- ⚠️ Sent with every request
"""
        
        elif auth_type == "api_key":
            doc += f"""## API Key Authentication

### Format
\`\`\`
{auth_config.get('header_name', 'X-API-Key')}: YOUR_API_KEY
\`\`\`

### Example
\`\`\`bash
curl -H "{auth_config.get('header_name', 'X-API-Key')}: your-api-key" https://api.example.com/resource
\`\`\`

### Python
\`\`\`python
import requests

headers = {auth_config.get('header_name', 'X-API-Key'): 'your-api-key'}
response = requests.get('https://api.example.com/resource', headers=headers)
\`\`\`
"""
        
        elif auth_type == "bearer":
            doc += """## Bearer Token Authentication

### Format
\`\`\`
Authorization: Bearer YOUR_TOKEN
\`\`\`

### Example
\`\`\`bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiI..." https://api.example.com/resource
\`\`\`

### Python
\`\`\`python
import requests

headers = {'Authorization': 'Bearer YOUR_TOKEN'}
response = requests.get('https://api.example.com/resource', headers=headers)
\`\`\`
"""
        
        elif auth_type == "oauth2":
            doc += f"""## OAuth 2.0 Authentication

### Authorization Endpoint
{auth_config.get('authorization_endpoint', 'https://auth.example.com/authorize')}

### Token Endpoint
{auth_config.get('token_endpoint', 'https://auth.example.com/token')}

### Scopes
{', '.join(auth_config.get('scopes', ['read', 'write']))}

### Flow
{auth_config.get('flow', 'authorization_code')}

### Implementation
1. Redirect user to authorization endpoint
2. User grants permission
3. Receive authorization code
4. Exchange code for access token
5. Use access token to call API

\`\`\`python
from authlib.integrations.requests_client import OAuth2Session

client = OAuth2Session(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_uri='https://yourapp.com/callback',
    authorize_url='https://auth.example.com/authorize',
    access_token_url='https://auth.example.com/token'
)
\`\`\`
"""
        
        return doc

    # ===== Private Methods =====

    def _validate_basic_auth(self, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate Basic authentication."""
        
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        
        issues = []
        
        if not username:
            issues.append("Username is required")
        if not password:
            issues.append("Password is required")
        
        if len(password) < 8:
            issues.append("Password is too weak (min 8 characters)")
        
        return {
            "is_valid": len(issues) == 0,
            "auth_type": "basic",
            "issues": issues,
            "security_notes": [
                "Credentials sent with every request",
                "Must use HTTPS",
                "Base64 encoding is not encryption"
            ]
        }

    def _validate_bearer_auth(self, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate Bearer token authentication."""
        
        token = credentials.get("token", "")
        
        issues = []
        
        if not token:
            issues.append("Token is required")
        
        if len(token) < 20:
            issues.append("Token appears too short")
        
        return {
            "is_valid": len(issues) == 0,
            "auth_type": "bearer",
            "issues": issues,
            "token_length": len(token)
        }

    def _validate_api_key_auth(self, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate API Key authentication."""
        
        key = credentials.get("key", "")
        location = credentials.get("location", "header")
        
        issues = []
        
        if not key:
            issues.append("API key is required")
        
        if len(key) < 16:
            issues.append("API key appears too short")
        
        if location == "query":
            issues.append("API key in query parameter is not secure - use header instead")
        
        return {
            "is_valid": len(issues) == 0,
            "auth_type": "api_key",
            "location": location,
            "issues": issues,
            "recommendations": ["Use header location", "Rotate keys regularly"]
        }

    def _validate_oauth2_auth(self, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate OAuth 2.0 authentication."""
        
        access_token = credentials.get("access_token", "")
        refresh_token = credentials.get("refresh_token")
        
        issues = []
        
        if not access_token:
            issues.append("Access token is required")
        
        return {
            "is_valid": len(issues) == 0,
            "auth_type": "oauth2",
            "has_refresh_token": bool(refresh_token),
            "issues": issues
        }

    def _validate_hmac_auth(self, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate HMAC authentication."""
        
        secret = credentials.get("secret", "")
        algorithm = credentials.get("algorithm", "sha256")
        
        issues = []
        
        if not secret:
            issues.append("Secret key is required")
        
        if len(secret) < 32:
            issues.append("Secret key should be at least 32 bytes")
        
        if algorithm not in ["sha256", "sha512"]:
            issues.append(f"Algorithm {algorithm} not recommended (use sha256 or sha512)")
        
        return {
            "is_valid": len(issues) == 0,
            "auth_type": "hmac",
            "algorithm": algorithm,
            "issues": issues
        }

    def _validate_jwt_auth(self, credentials: Dict, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate JWT authentication."""
        
        token = credentials.get("token", "")
        
        issues = []
        
        if not token:
            issues.append("Token is required")
        
        # Basic JWT format check
        parts = token.split(".")
        if len(parts) != 3:
            issues.append("Invalid JWT format (should have 3 parts)")
        
        return {
            "is_valid": len(issues) == 0,
            "auth_type": "jwt",
            "token_parts": len(parts) if "." in token else 0,
            "issues": issues
        }

    def _generate_hmac_headers(self, credentials: Dict) -> Dict[str, str]:
        """Generate HMAC signature headers."""
        
        secret = credentials.get("secret", "")
        algorithm = credentials.get("algorithm", "sha256")
        message = credentials.get("message", "")
        
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256 if algorithm == "sha256" else hashlib.sha512
        ).hexdigest()
        
        return {
            "X-Signature": signature,
            "X-Algorithm": algorithm,
            "X-Timestamp": str(int(time.time()))
        }

    def _get_auth_recommendations(self, schemes: List[str]) -> List[str]:
        """Get recommendations based on detected schemes."""
        
        recommendations = []
        
        if not schemes:
            recommendations.append("Implement authentication immediately")
        
        if "basic" in schemes:
            recommendations.append("Consider upgrading from Basic Auth to Bearer tokens")
        
        if "api_key" in schemes:
            recommendations.append("Implement API key rotation policy")
        
        if "oauth2" in schemes:
            recommendations.append("Use PKCE for public clients")
        
        if "jwt" in schemes:
            recommendations.append("Verify JWT signature and claims")
        
        recommendations.append("Use HTTPS exclusively")
        recommendations.append("Implement rate limiting")
        
        return recommendations


if __name__ == "__main__":
    handler = AuthHandler()
    
    # Test API key validation
    creds = {"key": "sk_test_1234567890abcdef", "location": "header"}
    result = handler.validate_credentials("api_key", creds)
    
    import json
    print(json.dumps(result, indent=2))
