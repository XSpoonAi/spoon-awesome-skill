---
name: Database Operations Manager
description: AI-powered database optimization, query analysis, schema design validation, and connection management. Analyzes SQL/NoSQL queries, recommends indexes, validates schema design patterns, and optimizes database performance.
version: 1.0.0
author: Skill Builder
tags:
  - database
  - optimization
  - sql
  - nosql
  - performance
  - query-analysis
  - schema-design

activation_triggers:
  - keyword: "analyze database"
  - keyword: "optimize query"
  - keyword: "database performance"
  - pattern: "query_analysis|schema_validation|pool_management"
  - intent: "improve_database_performance"

parameters:
  - name: query_input
    type: string
    required: true
    description: "SQL or NoSQL query to analyze (SELECT, INSERT, JOIN, aggregation, etc.)"
    example: "SELECT * FROM users WHERE age > 25"
  
  - name: analysis_type
    type: string
    required: true
    enum: ["query_optimization", "schema_analysis", "index_recommendation", "performance_metrics", "connection_pool"]
    description: "Type of database analysis to perform"
    example: "query_optimization"
  
  - name: database_type
    type: string
    required: true
    enum: ["mysql", "postgresql", "mongodb", "sqlite", "mariadb"]
    description: "Target database system"
    example: "mysql"
  
  - name: table_stats
    type: object
    required: false
    description: "Optional table statistics for performance estimation"
    example: { "row_count": 1000000, "avg_row_size": 512 }
  
  - name: optimization_level
    type: string
    required: false
    enum: ["basic", "intermediate", "aggressive"]
    default: "intermediate"
    description: "Level of optimization suggestions"
    example: "intermediate"

scripts:
  - name: query_builder
    type: python
    path: scripts/query_builder.py
    description: "Builds optimized SQL/NoSQL queries with execution plans and cost estimation"
    confidence: "92%"
    params: ["query_input", "database_type", "table_stats"]
  
  - name: schema_analyzer
    type: python
    path: scripts/schema_analyzer.py
    description: "Validates database schema design, normalization, and relationship integrity"
    confidence: "90%"
    params: ["database_type", "optimization_level"]
  
  - name: optimizer
    type: python
    path: scripts/optimizer.py
    description: "Detects optimization opportunities and recommends index strategies"
    confidence: "88%"
    params: ["query_input", "database_type", "table_stats"]
  
  - name: connection_manager
    type: python
    path: scripts/connection_manager.py
    description: "Manages connection pools, sizing, and lifecycle for optimal performance"
    confidence: "91%"
    params: ["database_type", "optimization_level"]

capabilities:
  - Query optimization (SELECT, INSERT, JOIN, aggregation)
  - SQL/NoSQL query analysis
  - Index recommendation engine
  - Schema design validation
  - Database normalization assessment (1NF, 2NF, 3NF)
  - Connection pool management
  - Performance metrics estimation
  - Cost analysis for queries
  - Relationship integrity checking
  - Execution plan generation

cache: true
composable: true

security_considerations:
  - Validate SQL inputs to prevent injection attacks
  - Don't expose sensitive database credentials
  - Use parameterized queries
  - Implement proper access control for schema changes
  - Monitor query execution time for DoS detection
  - Sanitize user inputs in dynamic queries
  - Use connection pooling for efficient resource utilization
  - Implement proper error handling without exposing internals
---

## Usage Examples

### Query Optimization
```python
from scripts.query_builder import QueryBuilder

builder = QueryBuilder()
optimized = builder.optimize_query(
    "SELECT * FROM users WHERE age > 25",
    database_type="postgresql"
)
print(f"Original cost: {optimized['original_cost']}")
print(f"Optimized cost: {optimized['optimized_cost']}")
```

### Schema Analysis
```python
from scripts.schema_analyzer import SchemaAnalyzer

analyzer = SchemaAnalyzer()
schema_report = analyzer.analyze_schema({
    "tables": ["users", "orders", "products"],
    "database_type": "mysql"
})
print(f"Normalization: {schema_report['normalization_level']}")
```

### Index Recommendations
```python
from scripts.optimizer import Optimizer

optimizer = Optimizer()
recommendations = optimizer.recommend_indexes(
    "SELECT * FROM orders WHERE user_id = 123",
    database_type="postgresql"
)
print(f"Suggested indexes: {recommendations['indexes']}")
```

### Connection Pool Management
```python
from scripts.connection_manager import ConnectionManager

pool = ConnectionManager()
config = pool.optimize_pool_size(
    database_type="mysql",
    expected_connections=1000
)
print(f"Pool size: {config['pool_size']}")
```

## Output Format

All modules return structured JSON:

```json
{
  "analysis_type": "string",
  "original_query": "string",
  "optimized_query": "string",
  "performance_gain": "percentage",
  "index_recommendations": ["array"],
  "execution_plan": "string",
  "estimated_cost": number,
  "normalization_status": "1NF|2NF|3NF",
  "recommendations": ["array of actionable items"]
}
```

## Severity Levels

| Level | Meaning | Impact | Action |
|-------|---------|--------|--------|
| CRITICAL | SQL injection vulnerability or data loss risk | High risk | Fix immediately |
| HIGH | Query performance issue causing slowdowns | Moderate risk | Optimize within sprint |
| MEDIUM | Schema normalization concern | Low-moderate risk | Plan refactoring |
| LOW | Minor optimization opportunity | Low risk | Consider for future |

## Version & Support

- **Version**: 1.0.0
- **Released**: February 2026
- **Status**: Production Ready
- **Confidence**: 90%

## Future Enhancements (v1.1.0)

- NoSQL optimization (MongoDB, DynamoDB)
- Sharding strategy recommendations
- Query caching suggestions
- Replication setup guidance
- Backup and recovery planning
- Multi-database migration tools
- Real-time performance monitoring integration
- Machine learning-based query prediction
