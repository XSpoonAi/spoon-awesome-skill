# Contributing to Spoon Awesome Skill

Thank you for your interest in contributing! This guide will help you submit high-quality skills.

## Skill Challenge Tracks

**Submissions are open for all challenge tracks.** SpoonOS Skills is the foundational collection (not a challenge track), but you can still submit issues and PRs for improvements.

| Challenge Track | Directory | Purpose | Status |
|-----------------|-----------|---------|--------|
| Web3 Data Intelligence | `web3-data-intelligence/` | On-chain analysis & insights | 🔵 Open for Submissions |
| Web3 Core Operations | `web3-core-operations/` | Smart contracts & protocols | 🔵 Open for Submissions |
| AI-Enhanced Productivity | `ai-productivity/` | API & automation skills | 🔵 Open for Submissions |
| Enterprise & Team | `enterprise-skills/` | Code quality & collaboration | 🔵 Open for Submissions |
| Platform Challenge | `platform-challenge/` | Skill routing & coverage | 🆕 Meta |

| Core Collection | Directory | Purpose | Status |
|-----------------|-----------|---------|--------|
| SpoonOS Skills | `spoonos-skills/` | Agent development patterns | 🟢 Issues/PRs welcome |

## Directory Structure

**Submit your PRs directly to the corresponding track directory.** You may also create your own sub-categories to organize your skills.

```
spoon-awesome-skill/
├── spoonos-skills/              # SpoonOS framework skills (Issues/PRs welcome)
│   └── your-skill/
├── web3-data-intelligence/      # On-chain analysis (Data Intelligence Track)
│   ├── onchain-analysis/        # Existing category
│   ├── security-analysis/       # Existing category
│   └── your-new-category/       # Create your own sub-category!
├── web3-core-operations/        # Protocol interactions (Core Operations Track)
│   ├── defi/                    # Existing category
│   └── your-new-category/       # Create your own sub-category!
├── ai-productivity/             # AI automation (Productivity Track)
│   └── your-skill-or-category/
├── enterprise-skills/           # Team tools (Enterprise Track)
│   └── your-skill-or-category/
├── platform-challenge/          # Meta improvements (Platform Track)
│   └── submissions/
│       └── your-name/
├── CONTRIBUTING.md
└── README.md
```

### Submission Options

1. **Add to existing category**: Submit your skill to an existing sub-directory
2. **Create new category**: Create a new sub-directory for a new skill category
3. **Direct submission**: Submit a single skill directly to the track directory

## Skill Format

Each skill MUST follow this structure:

```
your-skill/
├── SKILL.md              # Required: Skill definition
├── README.md             # Required: Detailed documentation
├── scripts/              # Optional: Python tool implementations
│   ├── main_tool.py      # Primary tool implementation
│   └── helper.py         # Helper scripts
└── references/           # Optional: Additional docs
    └── api_reference.md
```

### SKILL.md (Required)

```yaml
---
name: your-skill-name
description: Brief description (used for skill triggering). Max 200 chars.
version: 1.0.0
author: Your Name <your@email.com>
tags: [tag1, tag2, tag3]
---

# Skill Name

Brief overview (2-3 sentences).

## Quick Start

[Minimal working example - under 20 lines]

## Scripts

| Script | Purpose |
|--------|---------|
| [main_tool.py](scripts/main_tool.py) | Description |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | Your API key |

## Best Practices

1. Practice 1
2. Practice 2
```

### README.md (Required)

Detailed documentation including:
- Full API documentation
- All configuration options
- Error handling
- Examples for each use case

### Scripts (Optional)

If your skill includes Python tools, they should follow SpoonOS patterns:

```python
#!/usr/bin/env python3
"""
Tool Name - Brief description.

Author: Your Name
Version: 1.0.0
"""

from spoon_ai.tools.base import BaseTool
from pydantic import Field

class YourTool(BaseTool):
    name: str = "your_tool"
    description: str = "What this tool does"
    parameters: dict = Field(default={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Description"}
        },
        "required": ["param1"]
    })

    async def execute(self, param1: str) -> str:
        # Implementation
        return "Result"
```

## Pull Request Requirements

### 1. PR Title Format

```
[track] Add skill-name skill

Examples:
[web3-data-intelligence] Add token-analytics skill
[web3-core-operations] Add compound-lending skill
[ai-productivity] Add slack-integration skill
[enterprise-skills] Add code-review skill
[platform-challenge] Add skill-router tool
```

### 2. PR Description Template

Your PR description MUST include the following sections:

```markdown
## Skill Overview

- **Name**: your-skill-name
- **Track**: web3-data-intelligence / web3-core-operations / ai-productivity / enterprise-skills / platform-challenge
- **Description**: What this skill does

## Demo: Effect Demonstration

### Agent Configuration

We recommend using SpoonReactSkill, but you can also test with other skill-enabled agents like **Claude Code**.

**Option 1: SpoonReactSkill (Recommended)**
```python
from spoon_ai.agents import SpoonReactSkill

agent = SpoonReactSkill(
    name="demo_agent",
    skill_paths=["path/to/skills"],
    scripts_enabled=True
)
await agent.activate_skill("your-skill-name")
```

**Option 2: Claude Code**
```
# Copy skill to your workspace
cp -r your-skill/ .claude/skills/

# Or for agent workspace
cp -r your-skill/ .agent/skills/

# Then use the skill via Claude Code's skill system
```

### Input Prompt

```
[The exact prompt given to the agent]

Example:
"Check the current gas prices on Ethereum and suggest optimal transaction timing"
```

### Intermediate Outputs

Show the step-by-step execution:

```
Step 1: Agent activates skill "your-skill-name"
  → Tools loaded: [tool1, tool2]

Step 2: Agent calls tool1 with params: {"chain": "ethereum"}
  → Output: {"gas_price": "25 gwei", "timestamp": "..."}

Step 3: Agent processes result and calls tool2
  → Output: {"recommendation": "..."}
```

### Final Output

```
[The final response from the agent]

Example:
"Current Ethereum gas prices:
- Base Fee: 25 gwei
- Priority Fee: 2 gwei
- Estimated Cost: $3.50 for simple transfer

Recommendation: Gas prices are moderate. Good time for non-urgent transactions."
```

### Screenshots (Required)

**You MUST include screenshots showing the running example output.**

Attach screenshots that clearly show:
1. The agent running with your skill loaded
2. The input prompt being processed
3. Tool execution and intermediate outputs
4. The final response from the agent

Example screenshot requirements:
- Terminal/console output showing execution
- Clear, readable text
- Full output visible (no truncation)

## Checklist

- [ ] SKILL.md follows the required format
- [ ] README.md includes detailed documentation
- [ ] Scripts (if included) follow SpoonOS BaseTool pattern
- [ ] Environment variables documented (if applicable)
- [ ] **Screenshots of running example included**
- [ ] No API keys or secrets committed

### 3. Required Demo Evidence

Your PR MUST demonstrate the skill working with a skill-enabled agent. Include:

| Requirement | Description |
|-------------|-------------|
| **Agent Used** | SpoonReactSkill (recommended), Claude Code, or other skill-enabled agent |
| **Input Prompt** | The exact user query |
| **Skill Activation** | How the skill was activated |
| **Tool Calls** | Which tools were called with what parameters |
| **Intermediate Results** | Step-by-step outputs from each tool |
| **Final Output** | The complete agent response |

### Example Demo Format

```
═══════════════════════════════════════════════════════════════════
                    SKILL DEMO: gas-tracker
═══════════════════════════════════════════════════════════════════

AGENT: SpoonReactSkill
MODEL: gpt-4o
SKILLS LOADED: ["gas-tracker"]

───────────────────────────────────────────────────────────────────
INPUT PROMPT:
───────────────────────────────────────────────────────────────────
"What are the current gas prices on Ethereum? Should I send my
transaction now or wait?"

───────────────────────────────────────────────────────────────────
EXECUTION TRACE:
───────────────────────────────────────────────────────────────────

[Step 1] Skill Activation
  → Activated: gas-tracker
  → Tools available: [get_gas_price, get_gas_history, estimate_cost]

[Step 2] Tool Call: get_gas_price
  → Input: {"chain": "ethereum"}
  → Output: {
      "base_fee": "23.5 gwei",
      "priority_fee": "1.5 gwei",
      "total": "25 gwei",
      "usd_per_transfer": "$2.80"
    }

[Step 3] Tool Call: get_gas_history
  → Input: {"chain": "ethereum", "hours": 24}
  → Output: {
      "avg_24h": "35 gwei",
      "min_24h": "18 gwei",
      "max_24h": "85 gwei",
      "current_percentile": 28
    }

[Step 4] Agent Reasoning
  → "Current gas (25 gwei) is below 24h average (35 gwei)"
  → "At 28th percentile - relatively cheap"

───────────────────────────────────────────────────────────────────
FINAL OUTPUT:
───────────────────────────────────────────────────────────────────

📊 **Ethereum Gas Report**

**Current Prices:**
- Base Fee: 23.5 gwei
- Priority Fee: 1.5 gwei
- Total: 25 gwei (~$2.80 for transfer)

**24h Analysis:**
- Average: 35 gwei
- Range: 18 - 85 gwei
- Current: 28th percentile (cheaper than 72% of last 24h)

**Recommendation:** ✅ Good time to transact!
Current prices are 29% below the 24h average. If your transaction
isn't urgent, you could wait for potential dips below 20 gwei
during off-peak hours (typically 2-6 AM UTC).

═══════════════════════════════════════════════════════════════════
```

## Code Quality Requirements

### Python Standards

- Python 3.10+ compatible
- Type hints required
- Docstrings for all classes and public methods
- Async/await for I/O operations
- Error handling with meaningful messages

### Security Requirements

- NO hardcoded API keys or secrets
- All sensitive data via environment variables
- Input validation on all parameters
- Safe error messages (no stack traces to users)

## Review Process

1. **Automated Checks**: CI validates structure and format
2. **Code Review**: Maintainers review code quality
3. **Demo Verification**: We verify the effect demonstration works
4. **Documentation Review**: Ensure docs are clear and complete

## Getting Help

- Open an issue for questions
- Join our Discord for discussions
- Tag maintainers in PR for urgent reviews

## License

By contributing, you agree that your contributions will be licensed under MIT License.
