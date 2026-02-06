## Skill Overview

This skill is part of the SpoonOS Skills Micro Challenge submission, providing production-ready functionality with comprehensive error handling and JSON-based I/O.

## Features

- ✅ Full business logic implementation
- ✅ Demo mode with realistic sample data
- ✅ JSON parameter input validation
- ✅ Comprehensive error handling
- ✅ Self-contained and executable

## Usage

### Demo Mode
```bash
python scripts/main.py --demo
```

### With Parameters
```bash
python scripts/main.py --params '{"key": "value"}'
```

## Testing

This skill has been fully tested and validated for production use. Testing was performed using SpoonReactSkill and other skill-enabled agents like Claude Code.

### Demo Output
```
{"ok": true, "data": {"demo": true, "schema_type": "openapi", "diff": {"breaking_changes": [{"type": "removed_endpoint", "path": "/posts"}], "non_breaking_changes": [], "additions": [{"type": "new_endpoint", "path": "/comments"}, {"type": "new_method", "path": "/users", "method": "delete"}]}}}
```
