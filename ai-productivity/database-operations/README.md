# Database Operations Manager

AI-powered database optimization and management skill for analyzing queries, validating schema design, and optimizing database performance across SQL and NoSQL systems.

## Overview

The Database Operations Manager provides comprehensive database analysis and optimization capabilities:

- **Query Analysis & Optimization** - Analyzes SQL/NoSQL queries and recommends optimizations
- **Schema Design Validation** - Checks normalization, relationships, and design patterns
- **Index Recommendation** - Suggests optimal indexes for query performance
- **Connection Pool Management** - Configures optimal connection pooling strategies
- **Performance Metrics** - Estimates query costs and execution plans

## Architecture

### 4-Module System

```
Database Operations Manager
├── Query Builder (query_builder.py)
│   ├── SELECT query optimization
│   ├── INSERT/UPDATE batch operations
│   ├── JOIN analysis (INNER/LEFT/RIGHT/FULL)
│   ├── Aggregation queries
│   ├── NoSQL (MongoDB) support
│   └── Cost estimation
│
├── Schema Analyzer (schema_analyzer.py)
│   ├── Normalization assessment (1NF/2NF/3NF)
│   ├── Primary key validation
│   ├── Foreign key integrity
│   ├── Data type validation
│   ├── Relationship checking
│   └── Index analysis
│
├── Query Optimizer (optimizer.py)
│   ├── Query execution plan analysis
│   ├── Performance bottleneck detection
│   ├── Index recommendations
│   ├── Query rewriting suggestions
│   └── Cost-based optimization
│
└── Connection Manager (connection_manager.py)
    ├── Connection pool sizing
    ├── Load-based configuration
    ├── Pool health monitoring
    ├── Lifecycle management
    └── Framework-specific code generation
```

## Features

### Query Builder
Constructs and optimizes queries for different scenarios:
- SELECT with WHERE, ORDERBY, LIMIT, HAVING
- INSERT batch operations with optimal batch sizing
- JOIN queries (INNER, LEFT, RIGHT, FULL OUTER)
- Aggregation with GROUP BY and HAVING
- NoSQL aggregation pipelines

**Example:**
```python
builder = QueryBuilder()

# Build optimized SELECT
result = builder.build_select(
    table="orders",
    columns=["id", "customer_id", "total"],
    where={"status": "completed", "total": {">": 1000}},
    orderby={"created_at": "DESC"},
    limit=100
)
# Returns: optimized query + execution plan + cost metrics
```

### Schema Analyzer
Validates database schema design and relationships:
- Checks normalization levels (1NF, 2NF, 3NF)
- Validates primary and foreign keys
- Detects missing constraints
- Analyzes table relationships
- Recommends partitioning strategies

**Example:**
```python
analyzer = SchemaAnalyzer()

schema = {
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INT", "primary_key": True},
                {"name": "email", "type": "VARCHAR(255)", "unique": True},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        }
    ]
}

result = analyzer.analyze_schema(schema)
# Returns: health_score, normalization_level, issues with fixes
```

### Query Optimizer
Detects optimization opportunities:
- Identifies full table scans
- Detects SELECT * patterns
- Finds missing JOIN conditions
- Recommends indexes
- Estimates query costs

**Example:**
```python
optimizer = QueryOptimizer()

result = optimizer.optimize_query(
    query="SELECT * FROM users WHERE age > 25 ORDER BY created_at",
    table_stats={"row_count": 1000000}
)
# Returns: optimization suggestions, execution plan, performance impact
```

### Connection Manager
Manages database connection pools:
- Recommends pool size based on load
- Generates framework-specific config
- Monitors pool health
- Detects connection leaks

**Example:**
```python
manager = ConnectionPoolManager()

# Get recommendation
sizing = manager.recommend_pool_size(
    expected_concurrent_users=100,
    requests_per_second=500
)

# Generate config
config = manager.generate_config_code(
    pool_config=sizing,
    framework="sqlalchemy"
)
```

## Supported Databases

- **SQL**: MySQL, PostgreSQL, MariaDB, SQLite
- **NoSQL**: MongoDB (aggregation pipelines)

## Output Specifications

### Query Optimization Result
```json
{
  "original_query": "SELECT * FROM users WHERE id = 1",
  "optimized_query": "SELECT id, name, email FROM users WHERE id = 1",
  "issues_found": 1,
  "execution_plan": {
    "estimated_rows": 1,
    "estimated_cost": 0.0,
    "steps": [
      {"step": "Use index on 'id'", "cost_reduction": "95%"}
    ]
  },
  "performance_metrics": {
    "original_estimated_time_ms": 150,
    "optimized_estimated_time_ms": 1.5,
    "improvement_percent": 99
  }
}
```

### Schema Analysis Result
```json
{
  "health_score": 85,
  "normalization_level": "3NF",
  "total_tables": 10,
  "issues": [
    {
      "severity": "HIGH",
      "issue": "Missing primary key on table 'audit_log'",
      "fix": "ALTER TABLE audit_log ADD PRIMARY KEY (id)"
    }
  ],
  "optimization_potential": {
    "missing_indexes": 3,
    "denormalization_candidates": 1,
    "estimated_performance_gain": "15-20%"
  }
}
```

## Optimization Levels

**Basic**: Simple optimizations (indexes, obvious issues)
- Find missing primary keys
- Detect full table scans
- Recommend single-column indexes

**Intermediate** (Default): Balanced optimization
- Composite index recommendations
- Query rewriting suggestions
- Normalization analysis
- Connection pool sizing

**Aggressive**: Advanced optimizations
- Complex query restructuring
- Denormalization recommendations
- Partitioning strategies
- Custom execution plans

## Usage Examples

### Complete Query Analysis Workflow

```python
from scripts.query_builder import QueryBuilder
from scripts.optimizer import QueryOptimizer
from scripts.schema_analyzer import SchemaAnalyzer

# 1. Analyze the query
query = "SELECT u.id, u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.status = 'active' GROUP BY u.id"

optimizer = QueryOptimizer()
opt_result = optimizer.optimize_query(
    query=query,
    table_stats={"users_rows": 100000, "orders_rows": 1000000}
)

# 2. Build optimized version
builder = QueryBuilder()
optimized = builder.build_join_query(
    table1="users",
    table2="orders",
    join_type="LEFT",
    on_condition="u.id = o.user_id",
    columns=["u.id", "u.name", "COUNT(o.id)"]
)

# 3. Validate schema
schema = {...}  # Your schema definition
analyzer = SchemaAnalyzer()
schema_result = analyzer.analyze_schema(schema)

print(f"Performance Improvement: {opt_result['performance_metrics']['improvement_percent']}%")
```

### Connection Pool Configuration

```python
from scripts.connection_manager import ConnectionPoolManager

manager = ConnectionPoolManager()

# Get sizing recommendation
sizing = manager.recommend_pool_size(
    expected_concurrent_users=150,
    requests_per_second=1000
)

# Generate SQLAlchemy config
code = manager.generate_config_code(
    pool_config={
        "host": "db.example.com",
        "port": 3306,
        "database": "myapp",
        "pool_size": sizing["recommended_pool_size"],
        "max_overflow": sizing["recommended_max_overflow"]
    },
    framework="sqlalchemy"
)

print(code["sqlalchemy"])
```

## Performance Characteristics

| Operation | Avg Time | Query Size | Database |
|-----------|----------|-----------|----------|
| Query Analysis | 50-200ms | < 5KB | All |
| Schema Validation | 100-500ms | < 10 tables | All |
| Index Recommendation | 30-150ms | < 5KB | All |
| Pool Sizing | < 10ms | N/A | All |

## Common Optimizations

### 1. **Full Table Scan Detection**
- **Issue**: Query lacks WHERE clause
- **Fix**: Add conditions to limit result set
- **Impact**: 50-95% performance improvement

### 2. **SELECT * Anti-pattern**
- **Issue**: Fetching unnecessary columns
- **Fix**: Specify only required columns
- **Impact**: 10-30% performance improvement

### 3. **Missing Indexes**
- **Issue**: Queries on non-indexed columns
- **Fix**: Create composite indexes for frequent queries
- **Impact**: 50-1000x performance improvement

### 4. **Improper JOIN**
- **Issue**: Missing or incorrect JOIN conditions
- **Fix**: Ensure proper relationships defined
- **Impact**: Prevents incorrect results

### 5. **Subquery Optimization**
- **Issue**: Subqueries in IN clauses
- **Fix**: Replace with EXISTS or JOIN
- **Impact**: 2-10x performance improvement

## Integration Examples

### With Django ORM
```python
from scripts.optimizer import QueryOptimizer

# Analyze ORM-generated queries
query = str(User.objects.filter(age__gt=25).query)
optimizer = QueryOptimizer()
result = optimizer.optimize_query(query, database_type="mysql")
```

### With SQLAlchemy
```python
from scripts.query_builder import QueryBuilder

builder = QueryBuilder()
stmt = builder.build_select(
    table="users",
    columns=["id", "name"],
    where={"age": {">": 25}},
    limit=10
)
```

## Normalization Levels

- **1NF**: Atomic values, no repeating groups
- **2NF**: 1NF + no partial dependencies
- **3NF**: 2NF + no transitive dependencies (RECOMMENDED)
- **BCNF**: 3NF + no anomalies (STRICT)

## Health Score Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain current design |
| 75-89 | Good | Minor optimizations possible |
| 60-74 | Fair | Address identified issues |
| 40-59 | Poor | Significant refactoring needed |
| < 40 | Critical | Immediate intervention required |

## Deployment & Configuration

### Environment Variables
```bash
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=myapp
DB_USER=user
DB_PASSWORD=password
POOL_SIZE=20
MAX_OVERFLOW=30
```

### Docker Configuration
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## Performance Tips

1. **Use Connection Pooling**: Reduces connection overhead by 80-90%
2. **Index Key Columns**: Add indexes to WHERE, JOIN, and ORDER BY columns
3. **Normalize Schema**: Reduces data redundancy and update anomalies
4. **Batch Operations**: INSERT/UPDATE in batches of 100-1000 rows
5. **Avoid SELECT ***: Only fetch required columns
6. **Use EXPLAIN**: Always review execution plans before production

## Limitations

- Does not execute queries (analysis only)
- Requires actual table stats for accurate cost estimation
- Query rewriting suggestions may need DBA review
- NoSQL analysis limited to MongoDB aggregation pipelines

## Version & Support

- **Version**: 1.0.0
- **Last Updated**: 2024
- **Status**: Production Ready
- **Support**: Check repository issues and documentation

## Future Enhancements

- Query result set caching strategies
- Automatic sharding recommendations
- Machine learning-based cost estimation
- Real-time query performance monitoring
- Multi-database transaction support
- Query federation for distributed systems
