#!/usr/bin/env python3
"""
Connection Pool Manager
Manages database connections, pooling, and lifecycle
"""

from typing import Dict, List, Any
import time

class ConnectionPoolManager:
    """Manage database connection pools."""

    def __init__(self):
        self.pools = {}
        self.config_recommendations = {
            "small_app": {
                "pool_size": 5,
                "max_overflow": 10,
                "timeout": 30,
                "description": "Small app (< 10 concurrent users)"
            },
            "medium_app": {
                "pool_size": 20,
                "max_overflow": 30,
                "timeout": 30,
                "description": "Medium app (10-100 concurrent users)"
            },
            "large_app": {
                "pool_size": 50,
                "max_overflow": 100,
                "timeout": 30,
                "description": "Large app (100+ concurrent users)"
            },
            "high_traffic": {
                "pool_size": 100,
                "max_overflow": 200,
                "timeout": 15,
                "description": "High-traffic app (1000+ req/sec)"
            }
        }

    def create_pool(self, name: str, config: Dict) -> Dict[str, Any]:
        """Create a new connection pool."""
        
        pool_config = {
            "name": name,
            "driver": config.get("driver", "pymysql"),
            "host": config.get("host"),
            "port": config.get("port"),
            "database": config.get("database"),
            "pool_size": config.get("pool_size", 5),
            "max_overflow": config.get("max_overflow", 10),
            "pool_timeout": config.get("pool_timeout", 30),
            "pool_recycle": config.get("pool_recycle", 3600),
            "echo": config.get("echo", False)
        }
        
        self.pools[name] = pool_config
        
        return {
            "status": "CREATED",
            "pool_name": name,
            "configuration": pool_config,
            "connection_string": self._generate_connection_string(pool_config),
            "validation": self._validate_pool_config(pool_config)
        }

    def recommend_pool_size(self, expected_concurrent_users: int, requests_per_second: int) -> Dict[str, Any]:
        """Recommend pool size based on expected load."""
        
        # Formula: connections_needed = (expected_users * avg_query_time) + buffer
        avg_query_time = 0.1  # seconds
        connections_needed = int(expected_concurrent_users * avg_query_time * 1.2)
        
        # Adjust for request rate
        if requests_per_second > 1000:
            connections_needed = max(connections_needed, 100)
        elif requests_per_second > 100:
            connections_needed = max(connections_needed, 50)
        
        return {
            "expected_concurrent_users": expected_concurrent_users,
            "requests_per_second": requests_per_second,
            "recommended_pool_size": max(5, connections_needed),
            "recommended_max_overflow": max(10, connections_needed // 2),
            "preset_configs": self._get_preset_for_load(expected_concurrent_users)
        }

    def analyze_pool_health(self, pool_name: str, stats: Dict) -> Dict[str, Any]:
        """Analyze connection pool health."""
        
        active_connections = stats.get("active_connections", 0)
        total_size = stats.get("pool_size", 5)
        utilization = (active_connections / total_size * 100) if total_size > 0 else 0
        
        issues = []
        recommendations = []
        
        # Check utilization
        if utilization > 90:
            issues.append({
                "issue": "Pool near capacity",
                "severity": "CRITICAL",
                "utilization": f"{utilization:.1f}%"
            })
            recommendations.append("Increase pool_size immediately")
            recommendations.append("Check for connection leaks")
        elif utilization > 70:
            issues.append({
                "issue": "High pool utilization",
                "severity": "HIGH",
                "utilization": f"{utilization:.1f}%"
            })
            recommendations.append("Consider increasing pool_size")
        
        # Check for stale connections
        stale_threshold = 3600  # 1 hour
        stale_conns = stats.get("connections_older_than_hour", 0)
        if stale_conns > 0:
            issues.append({
                "issue": "Stale connections detected",
                "severity": "MEDIUM",
                "stale_count": stale_conns
            })
            recommendations.append("Set pool_recycle to 30 minutes")
        
        # Check wait times
        avg_wait = stats.get("average_wait_time_ms", 0)
        if avg_wait > 100:
            issues.append({
                "issue": "High connection wait time",
                "severity": "HIGH",
                "wait_time_ms": avg_wait
            })
            recommendations.append("Increase pool size or optimize queries")
        
        health_score = max(0, 100 - len(issues) * 20)
        
        return {
            "pool_name": pool_name,
            "health_score": health_score,
            "health_status": "HEALTHY" if health_score > 70 else "DEGRADED" if health_score > 40 else "CRITICAL",
            "utilization_percent": round(utilization, 1),
            "active_connections": active_connections,
            "pool_size": total_size,
            "issues": issues,
            "recommendations": recommendations,
            "metrics": {
                "average_wait_time_ms": avg_wait,
                "connection_errors_24h": stats.get("connection_errors", 0),
                "connections_recycled_24h": stats.get("recycled_connections", 0)
            }
        }

    def generate_config_code(self, pool_config: Dict, framework: str = "sqlalchemy") -> Dict[str, str]:
        """Generate configuration code for different frameworks."""
        
        configs = {}
        
        if framework == "sqlalchemy" or framework == "all":
            configs["sqlalchemy"] = f"""from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://{pool_config['host']}:{pool_config['port']}/{pool_config['database']}",
    pool_size={pool_config['pool_size']},
    max_overflow={pool_config['max_overflow']},
    pool_timeout={pool_config['pool_timeout']},
    pool_recycle={pool_config.get('pool_recycle', 3600)},
    echo={pool_config['echo']}
)"""
        
        if framework == "psycopg2" or framework == "all":
            configs["psycopg2"] = f"""import psycopg2
from psycopg2 import pool

conn_pool = pool.SimpleConnectionPool(
    {pool_config['pool_size']},
    {pool_config['pool_size'] + pool_config['max_overflow']},
    database="{pool_config['database']}",
    user="username",
    password="password",
    host="{pool_config['host']}",
    port={pool_config['port']}
)"""
        
        if framework == "django" or framework == "all":
            configs["django_settings"] = f"""DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{pool_config['database']}',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': '{pool_config['host']}',
        'PORT': {pool_config['port']},
        'CONN_MAX_AGE': 600,
        'OPTIONS': {{
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4'
        }}
    }}
}}"""
        
        return configs

    def _get_preset_for_load(self, concurrent_users: int) -> str:
        """Get preset configuration name for load level."""
        if concurrent_users < 10:
            return "small_app"
        elif concurrent_users < 100:
            return "medium_app"
        elif concurrent_users < 1000:
            return "large_app"
        else:
            return "high_traffic"

    def _validate_pool_config(self, config: Dict) -> Dict[str, Any]:
        """Validate pool configuration."""
        issues = []
        
        if config["pool_size"] < 1:
            issues.append("pool_size must be >= 1")
        
        if config["max_overflow"] < 0:
            issues.append("max_overflow must be >= 0")
        
        if config["pool_timeout"] < 1:
            issues.append("pool_timeout must be >= 1 second")
        
        return {
            "is_valid": len(issues) == 0,
            "validation_errors": issues or ["Configuration is valid"]
        }

    def _generate_connection_string(self, config: Dict) -> str:
        """Generate connection string."""
        driver = config.get("driver", "pymysql")
        user = config.get("user", "user")
        password = config.get("password", "password")
        host = config.get("host", "localhost")
        port = config.get("port", 3306)
        database = config.get("database", "dbname")
        
        return f"{driver}://{user}:{password}@{host}:{port}/{database}"


if __name__ == "__main__":
    manager = ConnectionPoolManager()
    
    # Create pool
    pool = manager.create_pool("main", {
        "host": "localhost",
        "port": 3306,
        "database": "myapp",
        "pool_size": 20,
        "max_overflow": 30
    })
    
    import json
    print(json.dumps(pool, indent=2))
