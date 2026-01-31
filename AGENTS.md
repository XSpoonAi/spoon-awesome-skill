# Repository Guidelines

## Project Structure & Module Organization

This repository is a curated collection of SpoonOS/Claude Code skills organized by track. Each skill lives in its own folder with required documentation and optional scripts.

- Top-level tracks: `spoonos-skills/`, `web3-data-intelligence/`, `web3-core-operations/`, `ai-productivity/`, `enterprise-skills/`, `platform-challenge/`.
- Typical skill layout:
  - `your-skill/SKILL.md` (required)
  - `your-skill/README.md` (required)
  - `your-skill/scripts/` (optional Python tools)
  - `your-skill/references/` (optional docs)

## Build, Test, and Development Commands

There is no repo-wide build. Testing is done per-skill with a skill-enabled agent.

- `python your_test_agent.py` runs a local SpoonReactSkill-based test (recommended).
- `cp -r your-skill/ .claude/skills/` copies a skill for Claude Code testing.
- `cp -r your-skill/ .agent/skills/` copies a skill into an agent workspace.

## Coding Style & Naming Conventions

- Python 3.10+; use type hints and docstrings for all classes/public methods.
- Use async/await for I/O in tools; handle errors with clear messages.
- Indentation: 4 spaces; follow standard PEP 8 formatting.
- Skill names and folders should be short, descriptive, and lowercase (e.g., `token-analytics`, `slack-integration`).
- Tool classes should extend `spoon_ai.tools.base.BaseTool` and declare `name`, `description`, and `parameters`.

## Testing Guidelines

- Prefer SpoonReactSkill for effect demonstrations and tool execution traces.
- Provide a minimal test agent script and run it locally (e.g., `python your_test_agent.py`).
- Ensure required environment variables are documented in `SKILL.md`.

## Commit & Pull Request Guidelines

- Commit messages follow a lightweight `type: summary` pattern (examples in history: `docs: ...`, `refactor: ...`).
- PR title format: `[track] Add skill-name skill` (e.g., `[ai-productivity] Add slack-integration skill`).
- PR descriptions must include a demo trace, final output, and **screenshots** of the running example.
- Include the checklist from `CONTRIBUTING.md` and avoid committing secrets.

## Security & Configuration Tips

- Never hardcode API keys; use environment variables and document them.
- Validate inputs in tools and avoid leaking stack traces in user-facing errors.
