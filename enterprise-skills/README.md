# Enterprise & Team Skills

**Track Focus:** Professional collaboration, project management, security compliance, and team productivity tools.

**Status**: Open for contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Available Skills

| Skill | Description | Status | Scripts |
|-------|-------------|--------|---------|
| [Code Review](./code-review/) | Automated code review and security scanning | 🔵 Accepting PRs | 0 |
| [Documentation](./documentation/) | Generate and update documentation | 🔵 Accepting PRs | 0 |
| [Refactoring](./refactoring/) | Code refactoring patterns | 🔵 Accepting PRs | 0 |
| [Debugging](./debugging/) | Debug assistance and analysis | 🔵 Accepting PRs | 0 |
| [Testing](./testing/) | Test generation and coverage | 🔵 Accepting PRs | 0 |
| [Performance](./performance/) | Performance analysis and optimization | 🔵 Accepting PRs | 0 |

### Status Legend

- 🟢 **Complete**: Production-ready with full documentation
- 🔵 **Accepting PRs**: Open for contributions
- 🔴 **WIP**: Work in progress

## Track Description

Enterprise & Team Skills focus on how individuals function within professional ecosystems:

- **Code Quality**: Automated review, security scanning, best practices
- **Collaboration**: Project management, documentation, knowledge sharing
- **DevSecOps**: Security compliance, vulnerability management
- **Productivity**: Debugging, testing, performance optimization

## Use Cases

1. **Automated PR Review**: Security scanning + style checking + optimization suggestions
2. **Incident Response**: Log analysis + root cause detection + fix recommendations
3. **Documentation**: Auto-generate READMEs, API docs, architecture diagrams
4. **Test Generation**: Create unit tests, integration tests, edge cases
5. **Performance Audit**: Profile code, identify bottlenecks, suggest optimizations

## Getting Started

```python
from spoon_ai.agents import SpoonReactSkill

agent = SpoonReactSkill(
    name="team_assistant",
    skill_paths=["./enterprise-skills"],
    scripts_enabled=True
)

# Example: "Review this PR for security issues and suggest improvements"
response = await agent.run("Review PR #123 for security issues and suggest improvements")
```

**Or with Claude Code:**
```bash
# Copy skills to your workspace
cp -r enterprise-skills/ .claude/skills/
```

## Skill Ideas (Welcome Contributions!)

### Code Review
- Style and convention checking
- Security vulnerability detection (OWASP Top 10)
- Performance anti-pattern detection
- Complexity analysis (cyclomatic, cognitive)
- PR review automation with suggested fixes

### Documentation
- README generation from code analysis
- API documentation (OpenAPI/Swagger)
- Changelog generation from commits
- Code comment generation
- Architecture diagrams (Mermaid/PlantUML)

### Refactoring
- Extract function/class patterns
- Rename across codebase
- Dead code removal
- Import optimization
- Pattern migration (e.g., callbacks to async/await)

### Debugging
- Error analysis and categorization
- Stack trace parsing with context
- Log analysis and correlation
- Memory leak detection
- Race condition detection

### Testing
- Unit test generation from code
- Integration test scaffolding
- Mock generation for dependencies
- Coverage analysis with gap detection
- Mutation testing for test quality

### Performance
- Profiling analysis and visualization
- Bottleneck detection and ranking
- Memory optimization suggestions
- Query optimization (SQL/NoSQL)
- Bundle size analysis (frontend)

## Challenge Track: Enterprise & Team Skills

**Goal:** Build skills that enhance team productivity and code quality at scale.

**High-Value Submissions:**
- AI-powered code review assistant
- Automatic changelog generator from commits
- Security vulnerability scanner with fix suggestions
- Test coverage analyzer with gap detection
- Performance regression detector
