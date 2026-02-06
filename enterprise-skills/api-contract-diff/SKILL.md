---
name: api-contract-diff
track: enterprise-skills
version: 0.1.0
summary: Compare OpenAPI/GraphQL schemas for breaking changes
---

## Description

Identify breaking changes, non-breaking changes, and additions between API schemas.

## Inputs

```json
{
  "schema_type": "openapi|graphql",
  "schema1": {...},
  "schema2": {...}
}
```

## Usage

```bash
python scripts/main.py --demo
```
