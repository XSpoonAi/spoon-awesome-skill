#!/usr/bin/env python3
import json
import argparse
import sys
from typing import Dict, Any, List


def format_success(data: Dict[str, Any]) -> str:
    return json.dumps({"ok": True, "data": data}, ensure_ascii=False)


def format_error(error: str, details=None) -> str:
    result = {"ok": False, "error": error}
    if details:
        result["details"] = details
    return json.dumps(result, ensure_ascii=False)


def generate_ci_checklist(skill_name: str, track: str) -> Dict[str, Any]:
    """Generate CI/CD checklist for skill validation."""
    checklist = {
        "skill": skill_name,
        "track": track,
        "checks": [
            {
                "category": "Structure",
                "items": [
                    {"check": "SKILL.md exists", "required": True},
                    {"check": "README.md exists", "required": True},
                    {"check": "scripts/main.py exists", "required": True},
                    {"check": "YAML frontmatter valid", "required": True}
                ]
            },
            {
                "category": "Functionality",
                "items": [
                    {"check": "--demo mode works", "required": True},
                    {"check": "--params mode works", "required": True},
                    {"check": "JSON output valid", "required": True},
                    {"check": "Error handling present", "required": True}
                ]
            },
            {
                "category": "Documentation",
                "items": [
                    {"check": "Usage examples provided", "required": True},
                    {"check": "Input/output documented", "required": True},
                    {"check": "Description clear", "required": True}
                ]
            },
            {
                "category": "Code Quality",
                "items": [
                    {"check": "No syntax errors", "required": True},
                    {"check": "Proper imports", "required": True},
                    {"check": "Error messages helpful", "required": False}
                ]
            }
        ]
    }
    
    return checklist


def main():
    parser = argparse.ArgumentParser(description='Generate CI/CD checklist for skill validation')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--params', type=str, help='JSON parameters')
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            checklist = generate_ci_checklist("api-webhook-signer", "ai-productivity")
            result = {
                "demo": True,
                "checklist": checklist,
                "total_checks": sum(len(cat["items"]) for cat in checklist["checks"])
            }
            print(format_success(result))
        
        elif args.params:
            params = json.loads(args.params)
            skill_name = params.get("skill_name", "")
            track = params.get("track", "ai-productivity")
            
            if not skill_name:
                raise ValueError("skill_name is required")
            
            checklist = generate_ci_checklist(skill_name, track)
            print(format_success(checklist))
        
        else:
            print(format_error("Either --demo or --params must be provided"))
            sys.exit(1)
    
    except json.JSONDecodeError as e:
        print(format_error(f"Invalid JSON: {e}"))
        sys.exit(1)
    except Exception as e:
        print(format_error(f"Unexpected error: {e}"))
        sys.exit(1)


if __name__ == '__main__':
    main()
