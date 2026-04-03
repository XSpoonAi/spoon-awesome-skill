#!/usr/bin/env python3
"""
API Rate Limiter Analyzer
Analyzes and manages API rate limiting strategies
"""

import time
from typing import Dict, List, Any, Optional
from collections import defaultdict

class RateLimiterAnalyzer:
    """Analyzes and configures API rate limiting."""

    def __init__(self):
        self.strategies = {
            "token_bucket": self._analyze_token_bucket,
            "sliding_window": self._analyze_sliding_window,
            "fixed_window": self._analyze_fixed_window,
            "leaky_bucket": self._analyze_leaky_bucket
        }

    def detect_rate_limit_headers(self, headers: Dict) -> Dict[str, Any]:
        """Detect rate limit information from response headers."""
        
        limits = {}
        
        # Common rate limit header patterns
        limit_headers = {
            "X-RateLimit-Limit": "limit",
            "X-RateLimit-Remaining": "remaining",
            "X-RateLimit-Reset": "reset",
            "X-Rate-Limit-Limit": "limit",
            "X-Rate-Limit-Remaining": "remaining",
            "X-Rate-Limit-Reset": "reset",
            "RateLimit-Limit": "limit",
            "RateLimit-Remaining": "remaining",
            "RateLimit-Reset": "reset"
        }
        
        detected_limits = {}
        
        for header, key in limit_headers.items():
            for h in headers:
                if h.lower() == header.lower():
                    detected_limits[key] = headers[h]
                    break
        
        # Parse the limits
        if "limit" in detected_limits:
            try:
                limits["requests_per_window"] = int(detected_limits["limit"])
            except ValueError:
                pass
        
        if "remaining" in detected_limits:
            try:
                limits["requests_remaining"] = int(detected_limits["remaining"])
            except ValueError:
                pass
        
        if "reset" in detected_limits:
            try:
                limits["reset_timestamp"] = int(detected_limits["reset"])
                limits["reset_in_seconds"] = max(0, int(detected_limits["reset"]) - int(time.time()))
            except ValueError:
                limits["reset_at"] = detected_limits["reset"]
        
        return {
            "detected_limits": limits,
            "headers_checked": list(limit_headers.keys()),
            "utilization": self._calculate_utilization(limits)
        }

    def analyze_rate_limit_strategy(self, strategy: str, config: Dict) -> Dict[str, Any]:
        """Analyze a rate limiting strategy."""
        
        if strategy not in self.strategies:
            return {
                "error": f"Unknown strategy: {strategy}",
                "supported_strategies": list(self.strategies.keys())
            }
        
        return self.strategies[strategy](config)

    def recommend_rate_limits(self, api_config: Dict) -> Dict[str, Any]:
        """Recommend rate limits based on API characteristics."""
        
        api_type = api_config.get("type", "general")
        expected_users = api_config.get("expected_concurrent_users", 100)
        request_complexity = api_config.get("request_complexity", "medium")
        
        # Calculate recommended limits
        base_rps = {
            "general": 1000,
            "public": 100,
            "internal": 5000,
            "webhook": 10000,
            "real_time": 500
        }.get(api_type, 1000)
        
        # Adjust based on complexity
        complexity_factor = {
            "simple": 1.5,
            "medium": 1.0,
            "complex": 0.5,
            "very_complex": 0.25
        }.get(request_complexity, 1.0)
        
        rps_limit = int(base_rps * complexity_factor)
        
        # Recommendations for different time windows
        recommendations = {
            "per_second": {
                "limit": max(1, rps_limit // 3600),
                "description": "Burst capacity limit"
            },
            "per_minute": {
                "limit": max(10, rps_limit // 60),
                "description": "Short-term capacity limit"
            },
            "per_hour": {
                "limit": rps_limit,
                "description": "Hourly capacity limit"
            },
            "per_day": {
                "limit": rps_limit * 24,
                "description": "Daily capacity limit"
            }
        }
        
        # Tier-based recommendations
        tiers = {
            "free": {
                "requests_per_day": rps_limit * 24 // 100,
                "burst_requests": max(1, rps_limit // 3600),
                "max_concurrent": 1
            },
            "pro": {
                "requests_per_day": rps_limit * 24 // 10,
                "burst_requests": max(10, rps_limit // 360),
                "max_concurrent": 5
            },
            "enterprise": {
                "requests_per_day": rps_limit * 24,
                "burst_requests": max(100, rps_limit // 36),
                "max_concurrent": 50
            }
        }
        
        return {
            "api_type": api_type,
            "expected_users": expected_users,
            "recommended_limits": recommendations,
            "tier_recommendations": tiers,
            "suggested_strategy": self._suggest_strategy(api_type)
        }

    def analyze_rate_limit_headers(self, headers: Dict) -> Dict[str, Any]:
        """Analyze rate limit headers for standards compliance."""
        
        standard_headers = {
            "X-RateLimit-Limit": "IETF standard",
            "X-RateLimit-Remaining": "IETF standard",
            "X-RateLimit-Reset": "IETF standard",
            "RateLimit-Limit": "W3C standard",
            "RateLimit-Remaining": "W3C standard",
            "RateLimit-Reset": "W3C standard"
        }
        
        found_headers = {}
        for header in standard_headers:
            if header in headers or any(h.lower() == header.lower() for h in headers):
                found_headers[header] = standard_headers[header]
        
        issues = []
        
        if not found_headers:
            issues.append({
                "severity": "HIGH",
                "issue": "No standard rate limit headers detected",
                "recommendation": "Implement X-RateLimit-* or RateLimit-* headers"
            })
        
        # Check for consistency
        if "X-RateLimit-Limit" in found_headers and "RateLimit-Limit" in found_headers:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Multiple rate limit header standards mixed",
                "recommendation": "Choose either X-RateLimit-* or RateLimit-* consistently"
            })
        
        return {
            "found_headers": found_headers,
            "standards_compliance": "COMPLIANT" if found_headers else "NOT_COMPLIANT",
            "issues": issues,
            "recommendations": self._get_header_recommendations(found_headers, issues)
        }

    def calculate_retry_strategy(self, rate_limit_info: Dict) -> Dict[str, Any]:
        """Calculate optimal retry strategy based on rate limits."""
        
        reset_in = rate_limit_info.get("reset_in_seconds", 60)
        remaining = rate_limit_info.get("requests_remaining", 0)
        
        if remaining > 0:
            return {
                "should_retry": False,
                "reason": "Requests still available"
            }
        
        # Exponential backoff strategy
        backoff_strategy = []
        for attempt in range(1, 6):
            wait_time = min(2 ** attempt + (attempt - 1), reset_in + 10)
            backoff_strategy.append({
                "attempt": attempt,
                "wait_seconds": wait_time,
                "wait_time_formatted": f"{wait_time}s"
            })
        
        # Check if reset is soon
        if reset_in < 60:
            simpler_strategy = {
                "strategy": "Simple wait",
                "wait_seconds": reset_in + 1,
                "reason": "Rate limit resets soon"
            }
        else:
            simpler_strategy = {
                "strategy": "Exponential backoff",
                "backoff": backoff_strategy
            }
        
        return {
            "should_retry": True,
            "reset_in_seconds": reset_in,
            "recommended_strategy": simpler_strategy,
            "max_retries": 5,
            "total_wait_time": sum(s["wait_seconds"] for s in backoff_strategy) if "backoff" in simpler_strategy else reset_in + 1
        }

    def generate_rate_limiter_code(self, strategy: str, config: Dict, language: str = "python") -> str:
        """Generate rate limiter implementation code."""
        
        if language == "python":
            return self._generate_python_rate_limiter(strategy, config)
        elif language == "javascript":
            return self._generate_js_rate_limiter(strategy, config)
        elif language == "typescript":
            return self._generate_ts_rate_limiter(strategy, config)
        
        return "# Unsupported language"

    # ===== Private Methods =====

    def _analyze_token_bucket(self, config: Dict) -> Dict[str, Any]:
        """Analyze token bucket rate limiting."""
        
        capacity = config.get("capacity", 100)
        refill_rate = config.get("refill_rate", 10)
        
        return {
            "strategy": "Token Bucket",
            "description": "Allows burst traffic up to capacity, then throttles to refill rate",
            "parameters": {
                "capacity": capacity,
                "refill_rate": f"{refill_rate} tokens/second"
            },
            "characteristics": {
                "burst_allowed": True,
                "burst_size": capacity,
                "steady_state_rps": refill_rate,
                "recovery_time": f"{capacity / refill_rate:.1f} seconds"
            },
            "best_for": ["APIs with bursty traffic", "CDN rate limiting", "Load balancing"],
            "implementation_complexity": "MEDIUM"
        }

    def _analyze_sliding_window(self, config: Dict) -> Dict[str, Any]:
        """Analyze sliding window rate limiting."""
        
        window_size = config.get("window_size_seconds", 60)
        limit = config.get("limit", 100)
        
        return {
            "strategy": "Sliding Window",
            "description": "Tracks requests in a rolling time window",
            "parameters": {
                "window_size": f"{window_size} seconds",
                "request_limit": limit,
                "requests_per_second": f"{limit / window_size:.2f}"
            },
            "characteristics": {
                "burst_allowed": False,
                "fair_distribution": True,
                "memory_overhead": "HIGH"
            },
            "best_for": ["Strict rate limiting", "Fair quota distribution", "User rate limits"],
            "implementation_complexity": "HIGH"
        }

    def _analyze_fixed_window(self, config: Dict) -> Dict[str, Any]:
        """Analyze fixed window rate limiting."""
        
        window_size = config.get("window_size_seconds", 60)
        limit = config.get("limit", 100)
        
        return {
            "strategy": "Fixed Window",
            "description": "Rate limit resets at fixed intervals",
            "parameters": {
                "window_size": f"{window_size} seconds",
                "request_limit": limit
            },
            "characteristics": {
                "burst_allowed": True,
                "burst_window": f"At window boundaries (up to {limit} requests)",
                "fairness": "POOR at window boundaries"
            },
            "best_for": ["Simple rate limiting", "API quotas", "Simple implementations"],
            "issues": ["Allows burst at window boundaries"],
            "implementation_complexity": "LOW"
        }

    def _analyze_leaky_bucket(self, config: Dict) -> Dict[str, Any]:
        """Analyze leaky bucket rate limiting."""
        
        capacity = config.get("capacity", 100)
        leak_rate = config.get("leak_rate", 10)
        
        return {
            "strategy": "Leaky Bucket",
            "description": "Queues requests and processes at constant rate",
            "parameters": {
                "bucket_capacity": capacity,
                "leak_rate": f"{leak_rate} requests/second"
            },
            "characteristics": {
                "queue_enabled": True,
                "max_queue_size": capacity,
                "processing_rate": leak_rate,
                "steady_state": "Guaranteed at leak_rate"
            },
            "best_for": ["Smooth traffic flow", "Request queuing", "Load smoothing"],
            "implementation_complexity": "MEDIUM"
        }

    def _suggest_strategy(self, api_type: str) -> str:
        """Suggest best rate limiting strategy for API type."""
        
        suggestions = {
            "general": "token_bucket",
            "public": "fixed_window",
            "internal": "leaky_bucket",
            "webhook": "token_bucket",
            "real_time": "token_bucket"
        }
        
        return suggestions.get(api_type, "token_bucket")

    def _calculate_utilization(self, limits: Dict) -> Optional[float]:
        """Calculate rate limit utilization percentage."""
        
        if "requests_per_window" in limits and "requests_remaining" in limits:
            limit = limits["requests_per_window"]
            remaining = limits["requests_remaining"]
            
            if limit > 0:
                return round((limit - remaining) / limit * 100, 1)
        
        return None

    def _get_header_recommendations(self, found_headers: Dict, issues: List) -> List[str]:
        """Get recommendations for rate limit headers."""
        
        recommendations = []
        
        if not found_headers:
            recommendations.append("Implement X-RateLimit-Limit header")
            recommendations.append("Implement X-RateLimit-Remaining header")
            recommendations.append("Implement X-RateLimit-Reset header")
        
        if issues:
            recommendations.append("Standardize on one header convention")
            recommendations.append("Document rate limit header format")
        
        return recommendations

    def _generate_python_rate_limiter(self, strategy: str, config: Dict) -> str:
        """Generate Python rate limiter code."""
        
        if strategy == "token_bucket":
            return """import time
from threading import Lock

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = Lock()
    
    def allow_request(self, tokens=1):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
"""
        
        elif strategy == "sliding_window":
            return """import time
from collections import deque
from threading import Lock

class SlidingWindow:
    def __init__(self, window_size, limit):
        self.window_size = window_size
        self.limit = limit
        self.requests = deque()
        self.lock = Lock()
    
    def allow_request(self):
        with self.lock:
            now = time.time()
            # Remove old requests outside window
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True
            return False
"""
        
        return "# Strategy not implemented"

    def _generate_js_rate_limiter(self, strategy: str, config: Dict) -> str:
        """Generate JavaScript rate limiter code."""
        
        if strategy == "token_bucket":
            return """class TokenBucket {
    constructor(capacity, refillRate) {
        this.capacity = capacity;
        this.tokens = capacity;
        this.refillRate = refillRate;
        this.lastRefill = Date.now();
    }
    
    allowRequest(tokens = 1) {
        const now = Date.now();
        const elapsed = (now - this.lastRefill) / 1000;
        this.tokens = Math.min(
            this.capacity,
            this.tokens + elapsed * this.refillRate
        );
        this.lastRefill = now;
        
        if (this.tokens >= tokens) {
            this.tokens -= tokens;
            return true;
        }
        return false;
    }
}
"""
        
        return "// Strategy not implemented"

    def _generate_ts_rate_limiter(self, strategy: str, config: Dict) -> str:
        """Generate TypeScript rate limiter code."""
        
        if strategy == "token_bucket":
            return """interface RateLimiterConfig {
    capacity: number;
    refillRate: number;
}

class TokenBucket {
    private capacity: number;
    private tokens: number;
    private refillRate: number;
    private lastRefill: number;
    
    constructor(config: RateLimiterConfig) {
        this.capacity = config.capacity;
        this.tokens = config.capacity;
        this.refillRate = config.refillRate;
        this.lastRefill = Date.now();
    }
    
    allowRequest(tokens: number = 1): boolean {
        const now = Date.now();
        const elapsed = (now - this.lastRefill) / 1000;
        this.tokens = Math.min(
            this.capacity,
            this.tokens + elapsed * this.refillRate
        );
        this.lastRefill = now;
        
        if (this.tokens >= tokens) {
            this.tokens -= tokens;
            return true;
        }
        return false;
    }
}
"""
        
        return "// Strategy not implemented"


if __name__ == "__main__":
    analyzer = RateLimiterAnalyzer()
    
    # Test rate limit detection
    headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "45",
        "X-RateLimit-Reset": "1640995200"
    }
    
    result = analyzer.detect_rate_limit_headers(headers)
    import json
    print(json.dumps(result, indent=2))
