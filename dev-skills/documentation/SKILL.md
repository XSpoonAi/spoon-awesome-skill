---
name: documentation-generator
description: Automatically generate project documentation from Python source code. Use when creating README, API docs, or architecture diagrams from docstrings and type hints.
---

# Documentation Generator

Generate professional documentation from Python source code using AST analysis.

## Quick Start

```bash
# Set environment variables
export PROJECT_PATH="./my_project"
export OUTPUT_DIR="./docs"

# Run generator
python scripts/doc_generator.py
```

## Generated Documentation

| Output | Description |
|--------|-------------|
| `README.md` | Project overview with structure summary |
| `API.md` | Function signatures, docstrings, type hints |
| `ARCHITECTURE.md` | Dependency graphs, class hierarchy |

## Usage

### As SpoonOS Tool

```python
from doc_generator import DocumentationGeneratorTool

tool = DocumentationGeneratorTool()

# Generate all docs
result = await tool.execute(
    project_path="./my_project",
    doc_type="all",
    output_dir="./docs"
)

# Generate specific type
result = await tool.execute(
    project_path="./my_project",
    doc_type="readme"  # or "api", "architecture"
)
```

### Standalone Function

```python
from doc_generator import generate_documentation

# Quick generation
generate_documentation("./my_project", doc_type="all", output_dir="./docs")
```

## Environment Variables

```bash
# Required
PROJECT_PATH=./my_project

# Optional
OUTPUT_DIR=./docs          # Default: ./docs
INCLUDE_PRIVATE=false      # Default: false
```

## Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to project root |
| `doc_type` | string | Yes | `readme`, `api`, `architecture`, or `all` |
| `output_dir` | string | No | Output directory (default: ./docs) |
| `include_private` | boolean | No | Include private methods (default: false) |

## AST Analysis Features

- **Classes**: Names, docstrings, methods, inheritance
- **Functions**: Signatures, parameters, return types
- **Imports**: Module dependencies for architecture graphs
- **Type Hints**: Full annotation parsing

## Best Practices

- Use [Google-style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) or [NumPy-style](https://numpydoc.readthedocs.io/en/latest/format.html) docstrings
- Add type hints to all function signatures
- Include `Args`, `Returns`, `Raises` sections in docstrings
- Keep module-level docstrings concise

## Customization

### Adding Custom Sections

```python
from doc_generator import DocumentationGeneratorTool

class CustomDocGenerator(DocumentationGeneratorTool):
    def _generate_readme(self, project_path, modules):
        readme = super()._generate_readme(project_path, modules)
        readme += "\n## Custom Section\n\nYour content here.\n"
        return readme
```

## References

- `scripts/doc_generator.py` - Core implementation with ASTAnalyzer
