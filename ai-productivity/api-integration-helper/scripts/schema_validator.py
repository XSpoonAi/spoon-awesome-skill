#!/usr/bin/env python3
"""
API Schema Validator
Validates and analyzes API request/response schemas
"""

import re
import json
from typing import Dict, List, Any
from enum import Enum

class DataType(Enum):
    """JSON Schema data types."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"

class SchemaValidator:
    """Validates and analyzes API schemas."""

    def __init__(self):
        self.json_schema_keywords = [
            "type", "properties", "required", "items", "minLength", "maxLength",
            "minimum", "maximum", "pattern", "enum", "default", "description",
            "format", "additionalProperties", "minItems", "maxItems"
        ]

    def validate_json_schema(self, schema: Dict) -> Dict[str, Any]:
        """Validate JSON schema structure."""
        
        issues = []
        warnings = []
        
        if not isinstance(schema, dict):
            issues.append({
                "severity": "CRITICAL",
                "issue": "Schema must be a dictionary",
                "fix": "Wrap schema in {}"
            })
            return {
                "is_valid": False,
                "issues": issues,
                "warnings": warnings,
                "validation_score": 0
            }
        
        # Check for required top-level keywords
        if "type" not in schema:
            warnings.append("Missing 'type' keyword - assume object type")
        
        # Validate properties
        if "properties" in schema:
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                issues.append({
                    "severity": "CRITICAL",
                    "issue": "properties must be a dictionary"
                })
            else:
                prop_issues = self._validate_properties(properties)
                issues.extend(prop_issues["issues"])
                warnings.extend(prop_issues["warnings"])
        
        # Validate required fields
        if "required" in schema:
            required = schema.get("required", [])
            if not isinstance(required, list):
                issues.append({
                    "severity": "CRITICAL",
                    "issue": "required must be an array"
                })
        
        # Validate items (for arrays)
        if "items" in schema:
            items_issues = self._validate_items(schema.get("items", {}))
            issues.extend(items_issues["issues"])
            warnings.extend(items_issues["warnings"])
        
        # Check for undefined properties
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for req_field in required:
            if req_field not in properties:
                issues.append({
                    "severity": "CRITICAL",
                    "issue": f"Required field '{req_field}' not defined in properties",
                    "fix": f"Add '{req_field}' to properties"
                })
        
        score = max(0, 100 - len(issues) * 20 - len(warnings) * 5)
        
        return {
            "is_valid": len(issues) == 0,
            "validation_score": score,
            "property_count": len(properties),
            "required_fields": len(required),
            "issues": issues,
            "warnings": warnings,
            "recommendations": self._get_schema_recommendations(schema, issues, warnings)
        }

    def validate_request_body(self, schema: Dict, sample_data: Dict) -> Dict[str, Any]:
        """Validate sample data against schema."""
        
        errors = []
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in sample_data:
                errors.append({
                    "field": field,
                    "error": f"Missing required field",
                    "severity": "CRITICAL"
                })
        
        # Check property types
        properties = schema.get("properties", {})
        for field, value in sample_data.items():
            if field in properties:
                prop_def = properties[field]
                expected_type = prop_def.get("type")
                type_error = self._check_type_match(value, expected_type)
                
                if type_error:
                    errors.append({
                        "field": field,
                        "value": str(value),
                        "expected_type": expected_type,
                        "actual_type": type(value).__name__,
                        "error": type_error,
                        "severity": "HIGH"
                    })
                
                # Check constraints
                constraint_errors = self._check_constraints(field, value, prop_def)
                errors.extend(constraint_errors)
        
        return {
            "is_valid": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "validation_coverage": self._calculate_coverage(schema, sample_data)
        }

    def compare_schemas(self, schema1: Dict, schema2: Dict) -> Dict[str, Any]:
        """Compare two API schemas for compatibility."""
        
        props1 = set(schema1.get("properties", {}).keys())
        props2 = set(schema2.get("properties", {}).keys())
        
        added = props2 - props1
        removed = props1 - props2
        common = props1 & props2
        
        breaking_changes = []
        
        # Check for removed required fields
        for field in removed:
            if field in schema1.get("required", []):
                breaking_changes.append({
                    "type": "REMOVED_REQUIRED_FIELD",
                    "field": field,
                    "impact": "Clients expecting this field will break"
                })
        
        # Check for type changes
        for field in common:
            type1 = schema1.get("properties", {}).get(field, {}).get("type")
            type2 = schema2.get("properties", {}).get(field, {}).get("type")
            
            if type1 != type2:
                breaking_changes.append({
                    "type": "TYPE_CHANGE",
                    "field": field,
                    "old_type": type1,
                    "new_type": type2,
                    "impact": "Serialization/deserialization may fail"
                })
        
        return {
            "breaking_changes": len(breaking_changes),
            "added_fields": list(added),
            "removed_fields": list(removed),
            "common_fields": list(common),
            "breaking_change_details": breaking_changes,
            "compatibility_status": "COMPATIBLE" if not breaking_changes else "INCOMPATIBLE",
            "recommendations": self._get_compatibility_recommendations(breaking_changes)
        }

    def generate_sample_data(self, schema: Dict) -> Dict[str, Any]:
        """Generate sample data matching schema."""
        
        return self._generate_sample_recursive(schema)

    def detect_schema_format(self, data: Dict) -> Dict[str, Any]:
        """Auto-detect schema from sample data."""
        
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field, value in data.items():
            schema["properties"][field] = self._infer_schema(value)
            schema["required"].append(field)
        
        return {
            "inferred_schema": schema,
            "confidence": "MEDIUM",
            "notes": "Review auto-detected schema and refine constraints",
            "recommendations": [
                "Add descriptions for all properties",
                "Define minLength/maxLength for strings",
                "Define minimum/maximum for numbers",
                "Add enum values if applicable",
                "Mark optional fields (remove from required)"
            ]
        }

    def generate_openapi_schema(self, schema: Dict, endpoint: str, method: str) -> str:
        """Generate OpenAPI schema definition."""
        
        openapi_schema = {
            "components": {
                "schemas": {
                    self._to_schema_name(endpoint): schema
                }
            },
            "paths": {
                endpoint: {
                    method.lower(): {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{self._to_schema_name(endpoint)}"}
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": f"#/components/schemas/{self._to_schema_name(endpoint)}"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return json.dumps(openapi_schema, indent=2)

    # ===== Private Methods =====

    def _validate_properties(self, properties: Dict) -> Dict[str, List]:
        """Validate properties definitions."""
        issues = []
        warnings = []
        
        for prop_name, prop_def in properties.items():
            if not isinstance(prop_def, dict):
                issues.append({
                    "severity": "CRITICAL",
                    "property": prop_name,
                    "issue": "Property definition must be an object"
                })
            
            if "type" not in prop_def and "$ref" not in prop_def:
                warnings.append({
                    "property": prop_name,
                    "issue": "Missing 'type' - inferred as 'string'",
                    "severity": "MEDIUM"
                })
            
            if "description" not in prop_def:
                warnings.append({
                    "property": prop_name,
                    "issue": "Missing description",
                    "severity": "LOW"
                })
        
        return {"issues": issues, "warnings": warnings}

    def _validate_items(self, items: Dict) -> Dict[str, List]:
        """Validate items definition for arrays."""
        issues = []
        warnings = []
        
        if "type" not in items:
            warnings.append({
                "issue": "items missing 'type'",
                "severity": "MEDIUM"
            })
        
        return {"issues": issues, "warnings": warnings}

    def _check_type_match(self, value: Any, expected_type: str) -> str:
        """Check if value matches expected type."""
        
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type and expected_type in type_map:
            expected = type_map[expected_type]
            if not isinstance(value, expected):
                return f"Expected {expected_type}, got {type(value).__name__}"
        
        return ""

    def _check_constraints(self, field: str, value: Any, prop_def: Dict) -> List[Dict]:
        """Check value against property constraints."""
        errors = []
        
        # String constraints
        if prop_def.get("type") == "string" and isinstance(value, str):
            min_len = prop_def.get("minLength")
            max_len = prop_def.get("maxLength")
            pattern = prop_def.get("pattern")
            
            if min_len and len(value) < min_len:
                errors.append({
                    "field": field,
                    "error": f"String too short (min {min_len})",
                    "severity": "MEDIUM"
                })
            
            if max_len and len(value) > max_len:
                errors.append({
                    "field": field,
                    "error": f"String too long (max {max_len})",
                    "severity": "MEDIUM"
                })
            
            if pattern and not re.match(pattern, value):
                errors.append({
                    "field": field,
                    "error": f"Value doesn't match pattern '{pattern}'",
                    "severity": "MEDIUM"
                })
        
        # Numeric constraints
        if prop_def.get("type") in ["integer", "number"] and isinstance(value, (int, float)):
            minimum = prop_def.get("minimum")
            maximum = prop_def.get("maximum")
            
            if minimum is not None and value < minimum:
                errors.append({
                    "field": field,
                    "error": f"Value below minimum ({minimum})",
                    "severity": "MEDIUM"
                })
            
            if maximum is not None and value > maximum:
                errors.append({
                    "field": field,
                    "error": f"Value above maximum ({maximum})",
                    "severity": "MEDIUM"
                })
        
        # Enum check
        if "enum" in prop_def and value not in prop_def["enum"]:
            errors.append({
                "field": field,
                "error": f"Value must be one of {prop_def['enum']}",
                "severity": "MEDIUM"
            })
        
        return errors

    def _calculate_coverage(self, schema: Dict, data: Dict) -> Dict[str, float]:
        """Calculate schema coverage percentage."""
        properties = schema.get("properties", {})
        fields_covered = sum(1 for field in properties if field in data)
        
        return {
            "covered_fields": fields_covered,
            "total_fields": len(properties),
            "coverage_percent": (fields_covered / len(properties) * 100) if properties else 0
        }

    def _generate_sample_recursive(self, schema: Dict) -> Any:
        """Recursively generate sample data."""
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "string":
            return schema.get("default", "sample_string")
        elif schema_type == "integer":
            return schema.get("default", 42)
        elif schema_type == "number":
            return schema.get("default", 3.14)
        elif schema_type == "boolean":
            return schema.get("default", True)
        elif schema_type == "array":
            items = schema.get("items", {})
            return [self._generate_sample_recursive(items)]
        elif schema_type == "object":
            sample = {}
            for prop, prop_def in schema.get("properties", {}).items():
                sample[prop] = self._generate_sample_recursive(prop_def)
            return sample
        
        return None

    def _infer_schema(self, value: Any) -> Dict:
        """Infer schema from a value."""
        
        if isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, str):
            return {"type": "string", "description": ""}
        elif isinstance(value, list):
            return {
                "type": "array",
                "items": self._infer_schema(value[0]) if value else {"type": "string"}
            }
        elif isinstance(value, dict):
            return {
                "type": "object",
                "properties": {k: self._infer_schema(v) for k, v in value.items()}
            }
        
        return {"type": "string"}

    def _get_schema_recommendations(self, schema: Dict, issues: List, warnings: List) -> List[str]:
        """Generate recommendations for schema."""
        recommendations = []
        
        if issues:
            recommendations.append("Fix all CRITICAL issues before deploying")
        
        if warnings:
            recommendations.append("Review and resolve MEDIUM/HIGH warnings")
        
        properties = schema.get("properties", {})
        for prop, prop_def in properties.items():
            if "description" not in prop_def:
                recommendations.append(f"Add description to property '{prop}'")
            
            if prop_def.get("type") == "string" and "minLength" not in prop_def:
                recommendations.append(f"Add minLength constraint to '{prop}'")
        
        return recommendations

    def _get_compatibility_recommendations(self, breaking_changes: List) -> List[str]:
        """Generate recommendations for schema changes."""
        recommendations = []
        
        if breaking_changes:
            recommendations.append("Consider versioning your API (v1, v2)")
            recommendations.append("Provide migration guide for clients")
            recommendations.append("Maintain backwards compatibility when possible")
            recommendations.append("Add deprecation warnings before removing fields")
        
        return recommendations

    def _to_schema_name(self, endpoint: str) -> str:
        """Convert endpoint to schema name."""
        name = endpoint.replace("/", "").replace("{", "").replace("}", "")
        return name.title() if name else "Schema"


if __name__ == "__main__":
    validator = SchemaValidator()
    
    # Test schema
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "User ID"},
            "name": {"type": "string", "minLength": 1, "maxLength": 100},
            "email": {"type": "string", "pattern": "^[^@]+@[^@]+$"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150}
        },
        "required": ["id", "name", "email"]
    }
    
    result = validator.validate_json_schema(schema)
    import json
    print(json.dumps(result, indent=2))
