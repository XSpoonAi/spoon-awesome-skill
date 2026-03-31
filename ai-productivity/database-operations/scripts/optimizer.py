#!/usr/bin/env python3
"""
Database Query Optimizer
Provides query optimization recommendations and execution plans
"""

from typing import Dict, List, Any

class QueryOptimizer:
    """Optimize database queries."""

    def optimize_query(self, query: str, table_stats: Dict = None) -> Dict[str, Any]:
        """Analyze and optimize a query."""
        
        issues = []
        recommendations = []
        optimized_query = query
        
        # Check for full table scans
        if "WHERE" not in query.upper():
            issues.append({
                "issue": "Full table scan",
                "severity": "HIGH",
                "recommendation": "Add WHERE clause to limit result set"
            })
        
        # Check for SELECT *
        if "SELECT *" in query.upper():
            issues.append({
                "issue": "SELECT * used",
                "severity": "MEDIUM",
                "recommendation": "Specify only needed columns to reduce network transfer",
                "optimization": "SELECT id, name, email ..."
            })
            optimized_query = optimized_query.replace("*", "id, name, email")
        
        # Check for JOIN without ON
        if "JOIN" in query.upper() and "ON" not in query.upper():
            issues.append({
                "issue": "JOIN without ON clause",
                "severity": "CRITICAL",
                "recommendation": "Add ON clause to prevent Cartesian product"
            })
        
        # Check for IN with subquery
        if "IN (SELECT" in query.upper():
            issues.append({
                "issue": "Subquery in IN clause",
                "severity": "MEDIUM",
                "recommendation": "Consider JOIN instead of IN subquery",
                "optimization": "Use INNER JOIN for better performance"
            })
        
        # Check for NOT IN with NULL
        if "NOT IN" in query.upper():
            issues.append({
                "issue": "NOT IN used",
                "severity": "LOW",
                "recommendation": "Consider NOT EXISTS or LEFT JOIN for NULL safety"
            })
        
        # Check for DISTINCT with GROUP BY
        if "DISTINCT" in query.upper() and "GROUP BY" in query.upper():
            issues.append({
                "issue": "Redundant DISTINCT with GROUP BY",
                "severity": "LOW",
                "recommendation": "Remove DISTINCT as GROUP BY already ensures uniqueness"
            })
        
        return {
            "original_query": query,
            "optimized_query": optimized_query,
            "issues_found": len(issues),
            "issues": issues,
            "execution_plan": self._generate_execution_plan(query, table_stats),
            "performance_metrics": self._estimate_performance(query, issues),
            "optimization_tips": self._get_optimization_tips(query)
        }

    def _generate_execution_plan(self, query: str, stats: Dict = None) -> Dict[str, Any]:
        """Generate execution plan."""
        plan_steps = []
        
        if "FROM" in query.upper():
            plan_steps.append("1. Access source table")
            plan_steps.append("2. Apply WHERE filters (if any)")
            plan_steps.append("3. Join with related tables (if any)")
            plan_steps.append("4. Apply GROUP BY/HAVING (if any)")
            plan_steps.append("5. Apply ORDER BY (if any)")
            plan_steps.append("6. Apply LIMIT/OFFSET (if any)")
        
        return {
            "steps": plan_steps,
            "estimated_rows_scanned": stats.get("table_rows", 1000000) if stats else 1000000,
            "estimated_rows_returned": stats.get("table_rows", 1000) if stats else 1000,
            "selectivity": 0.001  # 0.1% selectivity
        }

    def _estimate_performance(self, query: str, issues: List[Dict]) -> Dict[str, Any]:
        """Estimate query performance."""
        base_time = 100  # ms
        
        # Penalties
        for issue in issues:
            if issue["severity"] == "CRITICAL":
                base_time += 5000
            elif issue["severity"] == "HIGH":
                base_time += 1000
            elif issue["severity"] == "MEDIUM":
                base_time += 200
        
        return {
            "estimated_execution_time_ms": base_time,
            "performance_rating": self._rate_performance(base_time),
            "improvement_potential": min(base_time - 50, 5000),
            "estimated_improved_time_ms": max(50, base_time - min(base_time - 50, 5000))
        }

    def _rate_performance(self, execution_time: int) -> str:
        """Rate query performance."""
        if execution_time < 100:
            return "EXCELLENT"
        elif execution_time < 500:
            return "GOOD"
        elif execution_time < 2000:
            return "ACCEPTABLE"
        elif execution_time < 5000:
            return "SLOW"
        else:
            return "CRITICAL"

    def _get_optimization_tips(self, query: str) -> List[str]:
        """Get optimization tips."""
        tips = []
        
        tips.append("Add indexes on frequently queried columns")
        tips.append("Use EXPLAIN/ANALYZE to review actual execution plan")
        
        if "ORDER BY" in query.upper():
            tips.append("Ensure ORDER BY columns are indexed")
        
        if "LIKE" in query.upper():
            tips.append("Avoid LIKE with leading wildcard (e.g., %value)")
        
        if "OR" in query.upper():
            tips.append("Consider using UNION instead of multiple OR conditions")
        
        if "DISTINCT" in query.upper():
            tips.append("DISTINCT is expensive - use only when necessary")
        
        return tips

    def recommend_indexes(self, query: str) -> Dict[str, Any]:
        """Recommend indexes for query."""
        import re
        
        recommended_indexes = []
        
        # Extract WHERE columns
        where_match = re.search(r'WHERE\s+(.+?)(?:GROUP|ORDER|LIMIT|$)', query, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            columns = re.findall(r'(\w+)\s*[=<>!]', where_clause)
            for col in set(columns):
                recommended_indexes.append({
                    "type": "Single column",
                    "column": col,
                    "reason": "Used in WHERE clause",
                    "expected_improvement": "20-40%"
                })
        
        # Extract JOIN conditions
        join_match = re.findall(r'JOIN\s+\w+\s+ON\s+(.+?)(?:JOIN|WHERE|GROUP|$)', query, re.IGNORECASE)
        for condition in join_match:
            columns = re.findall(r'(\w+)\s*=', condition)
            for col in set(columns):
                recommended_indexes.append({
                    "type": "Foreign key",
                    "column": col,
                    "reason": "Used in JOIN condition",
                    "expected_improvement": "30-50%"
                })
        
        return {
            "total_recommendations": len(recommended_indexes),
            "indexes": recommended_indexes,
            "implementation_priority": "HIGH" if len(recommended_indexes) > 0 else "NONE"
        }


if __name__ == "__main__":
    optimizer = QueryOptimizer()
    
    test_query = "SELECT * FROM users WHERE status = 'active' ORDER BY created_at"
    
    result = optimizer.optimize_query(test_query)
    
    import json
    print(json.dumps(result, indent=2))
