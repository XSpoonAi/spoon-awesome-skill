# Documentation Generator Skill

Automatically generate professional documentation from Python source code with intelligent AST analysis.

## Overview

The Documentation Generator is a SpoonOS Skill that helps developers create comprehensive project documentation automatically. It analyzes Python source code using Abstract Syntax Trees (AST) to extract docstrings, type hints, and code structure information, then generates:

- **README.md** - Project overview with structure summary
- **API.md** - Detailed API documentation with function signatures
- **ARCHITECTURE.md** - Architecture diagrams and dependency graphs

## Features

✨ **Key Capabilities:**

- 📖 **Automatic README Generation** - Extract project info and create comprehensive READMEs
- 📚 **API Documentation** - Generate API docs from docstrings and type hints
- 🏗️ **Architecture Analysis** - Create dependency graphs and class hierarchies
- 🔍 **AST-based Analysis** - Extract code structure with precision
- ⚙️ **Configurable** - Control what to include (private methods, depth, etc.)
- 📝 **Multiple Formats** - Output as Markdown, HTML, or JSON

## Installation

### Requirements

- Python 3.10+
- SpoonOS Framework

### Setup

```bash
# Copy skill to dev-skills directory
cp -r documentation dev-skills/

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from doc_generator import DocumentationGeneratorTool

# Initialize tool
tool = DocumentationGeneratorTool()

# Generate all documentation
result = await tool.execute(
    project_path="./my_project",
    doc_type="all",
    output_dir="./docs"
)

print(result)  # ✅ Documentation generated successfully in ./docs
```

### Generate Specific Documentation Types

```python
# Generate only README
await tool.execute(
    project_path="./my_project",
    doc_type="readme",
    output_dir="./docs"
)

# Generate only API docs
await tool.execute(
    project_path="./my_project",
    doc_type="api",
    output_dir="./docs"
)

# Generate architecture documentation
await tool.execute(
    project_path="./my_project",
    doc_type="architecture",
    output_dir="./docs"
)
```

### Advanced Configuration

```python
# Include private methods
await tool.execute(
    project_path="./my_project",
    doc_type="all",
    output_dir="./docs",
    include_private=True
)
```

## API Reference

### DocumentationGeneratorTool

Main tool for generating documentation.

**Parameters:**
- `project_path` (str) - Path to project root directory
- `output_dir` (str) - Output directory for generated docs
- `doc_type` (str) - Type of documentation: "readme", "api", "architecture", or "all"
- `include_private` (bool) - Include private methods/functions

**Returns:**
- Success message or error description

### ASTAnalyzer

Internal class for analyzing Python source code.

**Methods:**
- `analyze_module(file_path: str)` - Analyze a single Python module
- `_extract_classes()` - Extract class information
- `_extract_functions()` - Extract function information
- `_extract_imports()` - Extract import statements

## Documentation Output Examples

### Generated README Structure

```markdown
# my_project

## Overview
Automatically generated documentation for the my_project...

## Project Structure
### module_name
Module description from docstring...

## Installation
```bash
pip install -r requirements.txt
```

## Usage
See [API Documentation](./API.md) for detailed usage.

## Contributing
Contributions are welcome! Please follow the coding standards.
```

### Generated API Documentation

```markdown
# API Documentation

## module_name
Module description...

### Classes

#### ClassName
Class description...

**Methods:**
- `method_name` - Method description

### Functions
- `function_name` - Function description
```

### Generated Architecture Documentation

```markdown
# Architecture Documentation

## Module Overview
- **module_name**: Module description

## Dependency Graph
module_name:
  ├─ external_lib
  └─ another_lib

## Class Hierarchy
- `ClassName` extends BaseClass
```

## Best Practices for Better Documentation

1. **Write Clear Docstrings**
   ```python
   def function_name(param1: str, param2: int) -> dict:
       """
       Brief description of what function does.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
           
       Examples:
           >>> function_name("test", 42)
           {'result': 'success'}
       """
       pass
   ```

2. **Use Type Hints**
   ```python
   from typing import List, Dict, Optional
   
   def process_data(items: List[Dict], config: Optional[Dict] = None) -> Dict:
       """Process data with proper type hints."""
       pass
   ```

3. **Organize Code Logically**
   - Group related functions and classes
   - Use meaningful module names
   - Maintain consistent structure

4. **Include Examples**
   - Add usage examples in docstrings
   - Show common patterns
   - Demonstrate error handling

## Limitations

- Currently supports Python source code analysis only
- Requires valid Python syntax
- Complex type annotations may not render perfectly
- Private members are excluded by default

## Troubleshooting

### "Project path does not exist"
Ensure the project path is absolute or relative to where the tool is executed.

### "Syntax error in module"
Check the Python file for syntax errors. The tool requires valid Python syntax.

### Missing documentation
Verify that docstrings exist in your code and follow PEP 257 conventions.

## Contributing

We welcome contributions! Please:

1. Follow PEP 8 style guidelines
2. Add docstrings to all functions/classes
3. Include type hints
4. Add unit tests for new features
5. Update this README with new features

## License

MIT License - See LICENSE file for details

## Author

**ETHPanda** - SpoonOS Skill Contributor

## Related Skills

- [Code Review](../code-review/) - Automated code review
- [Testing](../testing/) - Test generation
- [Refactoring](../refactoring/) - Code refactoring patterns

---

**Last Updated**: 2026-01-28  
**Version**: 1.0.0  
**Status**: Production Ready ✅
