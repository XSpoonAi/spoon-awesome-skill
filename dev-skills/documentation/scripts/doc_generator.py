#!/usr/bin/env python3
"""
Documentation Generator - Core module for generating project documentation.

Author: ETHPanda
Version: 1.0.0
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from pydantic import Field
from spoon_ai.tools.base import BaseTool


# Environment variable configuration
ENV_PROJECT_PATH = os.getenv("PROJECT_PATH", "")
ENV_OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./docs")
ENV_INCLUDE_PRIVATE = os.getenv("INCLUDE_PRIVATE", "false").lower() in ("true", "1", "yes")


class ASTAnalyzer:
    """Analyze Python source code using Abstract Syntax Trees."""

    def __init__(self, include_private: bool = False):
        """Initialize AST analyzer.
        
        Args:
            include_private: Whether to include private methods/functions.
        """
        self.include_private = include_private
        self.modules: Dict[str, Dict] = {}

    def analyze_module(self, file_path: str) -> Dict:
        """Analyze a Python module and extract documentation info.
        
        Args:
            file_path: Path to Python file.
            
        Returns:
            Dictionary with module information.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError as e:
                return {'error': f'Syntax error in {file_path}: {e}'}

        module_doc = ast.get_docstring(tree) or "No description provided."
        
        return {
            'name': Path(file_path).stem,
            'path': file_path,
            'docstring': module_doc,
            'classes': self._extract_classes(tree),
            'functions': self._extract_functions(tree),
            'imports': self._extract_imports(tree)
        }

    def _extract_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract class information from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.startswith('_') or self.include_private:
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "No description.",
                        'methods': self._extract_methods(node),
                        'bases': [self._get_name(base) for base in node.bases]
                    }
                    classes.append(class_info)
        
        return classes

    def _extract_methods(self, class_node: ast.ClassDef) -> List[Dict]:
        """Extract method information from class."""
        methods = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_') or self.include_private:
                    method_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "No description.",
                        'args': self._extract_args(node),
                        'returns': self._extract_returns(node)
                    }
                    methods.append(method_info)
        
        return methods

    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract top-level functions from module."""
        functions = []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_') or self.include_private:
                    func_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "No description.",
                        'args': self._extract_args(node),
                        'returns': self._extract_returns(node)
                    }
                    functions.append(func_info)
        
        return functions

    def _extract_args(self, func_node: ast.FunctionDef) -> List[Dict]:
        """Extract function arguments."""
        args = []
        
        for arg in func_node.args.args:
            arg_info = {
                'name': arg.arg,
                'annotation': self._get_name(arg.annotation) if arg.annotation else None
            }
            args.append(arg_info)
        
        return args

    def _extract_returns(self, func_node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        if func_node.returns:
            return self._get_name(func_node.returns)
        return None

    def _extract_imports(self, tree: ast.AST) -> List[Dict]:
        """Extract import statements."""
        imports = []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        'type': 'from',
                        'module': node.module,
                        'name': alias.name,
                        'alias': alias.asname
                    })
        
        return imports

    def _get_name(self, node: Optional[ast.expr]) -> Optional[str]:
        """Get the name of a type annotation."""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return None


class DocumentationGeneratorTool(BaseTool):
    """SpoonOS Tool for generating project documentation."""
    
    name: str = "generate_documentation"
    description: str = "Generate comprehensive documentation from Python source code including README, API docs, and architecture analysis"
    
    parameters: dict = Field(default={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "description": "Path to the project root directory"
            },
            "output_dir": {
                "type": "string",
                "description": "Output directory for generated docs (default: ./docs)"
            },
            "doc_type": {
                "type": "string",
                "enum": ["readme", "api", "architecture", "all"],
                "description": "Type of documentation to generate"
            },
            "include_private": {
                "type": "boolean",
                "description": "Include private methods and functions"
            }
        },
        "required": ["project_path", "doc_type"]
    })

    async def execute(
        self,
        project_path: str = ENV_PROJECT_PATH,
        doc_type: str = "all",
        output_dir: str = ENV_OUTPUT_DIR,
        include_private: bool = ENV_INCLUDE_PRIVATE
    ) -> str:
        """Execute documentation generation.
        
        Args:
            project_path: Path to project root
            doc_type: Type of documentation to generate
            output_dir: Output directory
            include_private: Include private members
            
        Returns:
            Generated documentation or status message
        """
        try:
            project_path = Path(project_path)
            output_dir = Path(output_dir)
            
            if not project_path.exists():
                return f"Error: Project path '{project_path}' does not exist"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            analyzer = ASTAnalyzer(include_private=include_private)
            modules = self._analyze_project(project_path, analyzer)
            
            if doc_type in ["readme", "all"]:
                readme = self._generate_readme(project_path, modules)
                with open(output_dir / "README.md", "w") as f:
                    f.write(readme)
            
            if doc_type in ["api", "all"]:
                api_doc = self._generate_api_docs(modules)
                with open(output_dir / "API.md", "w") as f:
                    f.write(api_doc)
            
            if doc_type in ["architecture", "all"]:
                arch_doc = self._generate_architecture(modules)
                with open(output_dir / "ARCHITECTURE.md", "w") as f:
                    f.write(arch_doc)
            
            return f"✅ Documentation generated successfully in {output_dir}"
            
        except Exception as e:
            return f"Error generating documentation: {e}"

    def _analyze_project(self, project_path: Path, analyzer: ASTAnalyzer) -> Dict:
        """Analyze all Python files in project."""
        modules = {}
        
        for py_file in project_path.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                module_info = analyzer.analyze_module(str(py_file))
                modules[str(py_file)] = module_info
        
        return modules

    def _generate_readme(self, project_path: Path, modules: Dict) -> str:
        """Generate README documentation."""
        readme = f"""# {project_path.name}

## Overview

Automatically generated documentation for the {project_path.name} project.

## Project Structure

"""
        
        for module_path, info in modules.items():
            if "error" not in info:
                readme += f"### {info['name']}\n\n{info['docstring']}\n\n"
        
        readme += """## Installation

```bash
pip install -r requirements.txt
```

## Usage

See [API Documentation](./API.md) for detailed usage.

## Contributing

Contributions are welcome! Please follow the coding standards.

---

*Generated by Documentation Generator Skill*
"""
        return readme

    def _generate_api_docs(self, modules: Dict) -> str:
        """Generate API documentation."""
        api_doc = "# API Documentation\n\n"
        
        for module_path, info in modules.items():
            if "error" in info:
                continue
                
            api_doc += f"## {info['name']}\n\n"
            api_doc += f"{info['docstring']}\n\n"
            
            if info['classes']:
                api_doc += "### Classes\n\n"
                for cls in info['classes']:
                    api_doc += f"#### {cls['name']}\n\n"
                    api_doc += f"{cls['docstring']}\n\n"
                    
                    if cls['methods']:
                        api_doc += "**Methods:**\n\n"
                        for method in cls['methods']:
                            api_doc += f"- `{method['name']}` - {method['docstring']}\n"
                    api_doc += "\n"
            
            if info['functions']:
                api_doc += "### Functions\n\n"
                for func in info['functions']:
                    api_doc += f"- `{func['name']}` - {func['docstring']}\n"
                api_doc += "\n"
        
        return api_doc

    def _generate_architecture(self, modules: Dict) -> str:
        """Generate architecture documentation."""
        arch_doc = "# Architecture Documentation\n\n"
        arch_doc += "## Module Overview\n\n"
        
        for module_path, info in modules.items():
            if "error" not in info:
                arch_doc += f"- **{info['name']}**: {info['docstring']}\n"
        
        arch_doc += "\n## Dependency Graph\n\n```\n"
        
        for module_path, info in modules.items():
            if "error" not in info and info['imports']:
                arch_doc += f"{info['name']}:\n"
                for imp in info['imports'][:3]:  # Limit to first 3
                    arch_doc += f"  ├─ {imp['module']}\n"
                arch_doc += "\n"
        
        arch_doc += "```\n\n## Class Hierarchy\n\n"
        
        for module_path, info in modules.items():
            if "error" not in info and info['classes']:
                for cls in info['classes']:
                    if cls['bases']:
                        arch_doc += f"- `{cls['name']}` extends {', '.join(cls['bases'])}\n"
        
        return arch_doc


# Convenience function
def generate_documentation(project_path: str, doc_type: str = "all", output_dir: str = "./docs") -> str:
    """Generate documentation for a project."""
    import asyncio
    
    tool = DocumentationGeneratorTool()
    return asyncio.run(tool.execute(project_path, doc_type, output_dir))
