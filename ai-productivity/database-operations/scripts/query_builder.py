#!/usr/bin/env python3
"""
SQL/NoSQL Query Builder
Generates optimized database queries for common operations
"""

from typing import Dict, List, Any

class QueryBuilder:
    """Build optimized database queries."""

    def __init__(self):
        self.operations = {
            "select": "SELECT {columns} FROM {table} {where} {orderby} {limit}",
            "insert": "INSERT INTO {table} ({columns}) VALUES ({values})",
            "update": "UPDATE {table} SET {updates} {where}",
            "delete": "DELETE FROM {table} {where}",
            "join": "SELECT {columns} FROM {table1} {join_type} JOIN {table2} ON {condition}",
            "aggregate": "SELECT {function}({column}) FROM {table} {groupby} {having}"
        }

    def build_select(self, table: str, columns: List[str] = None, where: Dict = None, 
                     orderby: str = None, limit: int = None) -> Dict[str, Any]:
        """Build SELECT query."""
        cols = ", ".join(columns) if columns else "*"
        
        query = f"SELECT {cols} FROM {table}"
        params = []
        
        if where:
            conditions = []
            for col, val in where.items():
                conditions.append(f"{col} = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        
        if orderby:
            query += f" ORDER BY {orderby}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return {
            "query": query,
            "parameters": params,
            "execution_plan": self._analyze_query(query),
            "estimated_cost": self._estimate_cost(query, where)
        }

    def build_insert_batch(self, table: str, rows: List[Dict]) -> Dict[str, Any]:
        """Build batch INSERT query."""
        if not rows:
            return {"error": "No rows provided"}
        
        columns = list(rows[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        params = []
        for row in rows:
            params.extend([row.get(col) for col in columns])
        
        return {
            "query": query,
            "parameters": params,
            "row_count": len(rows),
            "batch_size_recommendation": self._recommend_batch_size(len(rows))
        }

    def build_join_query(self, table1: str, table2: str, join_type: str = "INNER", 
                        on_condition: str = None, columns: List[str] = None) -> Dict[str, Any]:
        """Build JOIN query."""
        cols = ", ".join(columns) if columns else f"{table1}.*, {table2}.*"
        
        query = f"""SELECT {cols}
FROM {table1}
{join_type} JOIN {table2}
ON {on_condition}"""
        
        return {
            "query": query,
            "join_type": join_type,
            "execution_plan": "Hash join recommended" if len(cols) > 100 else "Nested loop acceptable"
        }

    def build_aggregation(self, table: str, aggregate_func: str, column: str,
                         groupby: str = None, having: str = None) -> Dict[str, Any]:
        """Build aggregation query."""
        query = f"SELECT {groupby}, {aggregate_func}({column}) FROM {table}"
        
        if groupby:
            query += f" GROUP BY {groupby}"
        
        if having:
            query += f" HAVING {having}"
        
        return {
            "query": query,
            "aggregation_function": aggregate_func,
            "indexed_recommendation": f"Index on {groupby if groupby else column}"
        }

    def build_nosql_query(self, collection: str, query_obj: Dict) -> Dict[str, Any]:
        """Build NoSQL (MongoDB) query."""
        return {
            "database_type": "MongoDB",
            "collection": collection,
            "query": query_obj,
            "aggregation_pipeline": self._to_aggregation_pipeline(query_obj),
            "optimization_tips": [
                "Add index on frequently queried fields",
                "Use projection to reduce document size",
                "Prefer aggregation pipeline over map-reduce"
            ]
        }

    def _analyze_query(self, query: str) -> str:
        """Analyze query execution plan."""
        if "JOIN" in query:
            return "Hash join recommended for large tables"
        elif "GROUP BY" in query:
            return "B-tree index on group column recommended"
        elif "WHERE" in query:
            return "Consider index on WHERE clause columns"
        return "Simple table scan"

    def _estimate_cost(self, query: str, filters: Dict = None) -> Dict[str, Any]:
        """Estimate query cost."""
        selectivity = 0.1 if filters else 1.0
        
        return {
            "io_cost": round(100 * selectivity, 2),
            "cpu_cost": round(50 * selectivity, 2),
            "total_cost": round(150 * selectivity, 2),
            "estimated_rows": f"~{int(1000000 * selectivity)} rows"
        }

    def _recommend_batch_size(self, row_count: int) -> str:
        """Recommend batch size for bulk operations."""
        if row_count < 100:
            return "1000 rows per batch"
        elif row_count < 10000:
            return "5000 rows per batch"
        else:
            return "10000 rows per batch (split into smaller transactions)"

    def _to_aggregation_pipeline(self, query_obj: Dict) -> List[Dict]:
        """Convert query object to aggregation pipeline."""
        return [
            {"$match": query_obj},
            {"$project": {"_id": 0}},
            {"$limit": 1000}
        ]


if __name__ == "__main__":
    builder = QueryBuilder()
    
    # Test SELECT
    select = builder.build_select(
        "users",
        columns=["id", "name", "email"],
        where={"status": "active"},
        orderby="created_at DESC",
        limit=10
    )
    
    import json
    print(json.dumps(select, indent=2))
