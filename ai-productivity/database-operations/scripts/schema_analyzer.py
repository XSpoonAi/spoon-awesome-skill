#!/usr/bin/env python3
"""
Database Schema Analyzer
Analyzes schema design and recommends optimizations
"""

from typing import Dict, List, Any

class SchemaAnalyzer:
    """Analyze database schema design."""

    def analyze_schema(self, tables: List[Dict]) -> Dict[str, Any]:
        """Analyze overall schema design."""
        issues = []
        recommendations = []
        
        for table in tables:
            table_issues = self._analyze_table(table)
            issues.extend(table_issues)
        
        # Check relationships
        relationship_issues = self._check_relationships(tables)
        issues.extend(relationship_issues)
        
        # Check normalization
        normalization_score = self._check_normalization(tables)
        
        # Calculate overall health
        health_score = max(0, 100 - len(issues) * 10)
        
        return {
            "schema_health_score": health_score,
            "total_issues": len(issues),
            "normalization_level": normalization_score,
            "table_count": len(tables),
            "issues": sorted(issues, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}.get(x.get("severity"), 3)),
            "recommendations": self._generate_recommendations(issues),
            "optimization_potential": self._calculate_optimization_potential(issues)
        }

    def _analyze_table(self, table: Dict) -> List[Dict]:
        """Analyze individual table design."""
        issues = []
        columns = table.get("columns", [])
        
        # Check for primary key
        if not any(col.get("primary_key") for col in columns):
            issues.append({
                "type": "missing_primary_key",
                "table": table.get("name"),
                "severity": "CRITICAL",
                "fix": "Add primary key column (id INT AUTO_INCREMENT PRIMARY KEY)"
            })
        
        # Check for proper data types
        for col in columns:
            col_type = col.get("type", "").upper()
            
            # VARCHAR without length
            if "VARCHAR" in col_type and "(" not in col_type:
                issues.append({
                    "type": "varchar_without_length",
                    "table": table.get("name"),
                    "column": col.get("name"),
                    "severity": "HIGH",
                    "fix": f"Change VARCHAR to VARCHAR(255) or appropriate length"
                })
            
            # Missing NOT NULL constraint
            if not col.get("nullable", True):
                issues.append({
                    "type": "nullable_column",
                    "table": table.get("name"),
                    "column": col.get("name"),
                    "severity": "MEDIUM",
                    "fix": "Add NOT NULL constraint if column always has value"
                })
        
        # Check for indexes
        if not table.get("indexes"):
            issues.append({
                "type": "no_indexes",
                "table": table.get("name"),
                "severity": "HIGH",
                "fix": "Add indexes on frequently queried columns"
            })
        
        # Check table size
        if table.get("rows", 0) > 10000000:
            issues.append({
                "type": "large_table",
                "table": table.get("name"),
                "rows": table.get("rows"),
                "severity": "MEDIUM",
                "fix": "Consider partitioning table by date range or category"
            })
        
        return issues

    def _check_relationships(self, tables: List[Dict]) -> List[Dict]:
        """Check foreign key relationships."""
        issues = []
        table_names = {t.get("name") for t in tables}
        
        for table in tables:
            foreign_keys = table.get("foreign_keys", [])
            
            for fk in foreign_keys:
                ref_table = fk.get("references")
                
                # Check if referenced table exists
                if ref_table not in table_names:
                    issues.append({
                        "type": "orphan_foreign_key",
                        "table": table.get("name"),
                        "foreign_key": fk.get("name"),
                        "severity": "CRITICAL",
                        "fix": f"Referenced table '{ref_table}' does not exist"
                    })
        
        return issues

    def _check_normalization(self, tables: List[Dict]) -> str:
        """Evaluate normalization level."""
        # Simplified check
        score = 0
        
        for table in tables:
            columns = table.get("columns", [])
            
            # Check for repeating groups (not properly normalized)
            if any(col.get("name", "").endswith("_1") or col.get("name", "").endswith("_2") 
                   for col in columns):
                score -= 20
            
            # Check for dependent columns (not 3NF)
            if self._has_dependent_columns(columns):
                score -= 15
            
            score += 25  # Base points
        
        score = min(100, max(0, score))
        
        if score >= 85:
            return "3NF (Third Normal Form)"
        elif score >= 60:
            return "2NF (Second Normal Form)"
        else:
            return "1NF (First Normal Form) - requires denormalization strategy"

    def _has_dependent_columns(self, columns: List[Dict]) -> bool:
        """Check for functionally dependent columns."""
        col_names = {col.get("name", "").lower() for col in columns}
        
        # Check for patterns like city/state/country where city determines state
        city_state_patterns = [
            ("city", "state"),
            ("state", "country"),
            ("employee_id", "department")
        ]
        
        for col1, col2 in city_state_patterns:
            if col1 in col_names and col2 in col_names:
                return True
        
        return False

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if any(i["type"] == "missing_primary_key" for i in issues):
            recommendations.append("Add primary keys to all tables for data integrity")
        
        if any(i["type"] == "no_indexes" for i in issues):
            recommendations.append("Add indexes on frequently queried and foreign key columns")
        
        if any(i["type"] == "large_table" for i in issues):
            recommendations.append("Implement table partitioning for large tables")
        
        if any(i["type"] == "varchar_without_length" for i in issues):
            recommendations.append("Use appropriate VARCHAR lengths to optimize storage")
        
        return recommendations

    def _calculate_optimization_potential(self, issues: List[Dict]) -> Dict[str, Any]:
        """Calculate potential performance improvement."""
        critical = sum(1 for i in issues if i.get("severity") == "CRITICAL")
        high = sum(1 for i in issues if i.get("severity") == "HIGH")
        
        potential_improvement = critical * 20 + high * 10
        
        return {
            "potential_improvement": min(50, potential_improvement),
            "priority_fixes": critical,
            "quick_wins": high
        }


if __name__ == "__main__":
    analyzer = SchemaAnalyzer()
    
    sample_schema = [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INT", "primary_key": True},
                {"name": "email", "type": "VARCHAR", "nullable": False},
                {"name": "created_at", "type": "TIMESTAMP"}
            ],
            "indexes": [{"name": "idx_email", "column": "email"}],
            "rows": 1000000
        }
    ]
    
    result = analyzer.analyze_schema(sample_schema)
    
    import json
    print(json.dumps(result, indent=2))
