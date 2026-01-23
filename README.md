# Spoon Awesome Skill

A curated collection of high-quality Claude Code skills for SpoonOS development and Web3 integrations.

**57 Python scripts** across **19 skills** covering agent development, blockchain interactions, and production deployment.

## Two Skill Collections, Two Purposes

### SpoonOS Skills → Vibe Coding

**Empower developers to build SpoonOS Agents and applications through Vibe Coding.**

Copy SpoonOS skills into `.claude/skills/` or `.agent/skills/` and describe what you want to build. The AI uses these skills to generate complete, production-ready SpoonOS agents and applications.

### Web3 Skills → Skill Agent Integrations

**Provide blockchain tools for SpoonOS `SpoonReactSkill` agents to use.**

Web3 skills contain executable scripts that become callable tools when loaded by a `SpoonReactSkill` agent. Your skill agent can automatically leverage DeFi protocols, security checks, DAO voting, and more.

```
┌──────────────────────────────────────────────────────────────────┐
│                         Developer                                │
├──────────────────────────────────────────────────────────────────┤
│                            │                                     │
│                      Vibe Coding                                 │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              SpoonOS Skills (.claude/skills/)            │    │
│  │  • Agent Development    • Graph Workflows                │    │
│  │  • Tool Development     • Platform Integration           │    │
│  │  • Deployment Guide     • Testing Patterns               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                     Generates                                    │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              SpoonReactSkill Agent                       │    │
│  │  skill_paths = [".agent/skills/web3-skills"]             │    │
│  │  scripts_enabled = True                                  │    │
│  │  auto_trigger_skills = True                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                      Loads Tools                                 │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Web3 Skills (.agent/skills/)                │    │
│  │  • DeFi Protocols → aave_lending, oneinch_swap          │    │
│  │  • Security → goplus_security, honeypot_check           │    │
│  │  • DAO → snapshot_vote, governor_vote                   │    │
│  │  • NFT → opensea_collection, nft_rarity                 │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### What You Can Build

| Agent Type | SpoonOS Skills Used | Web3 Skills Integrated |
|------------|---------------------|------------------------|
| **DeFi Trading Bot** | agent-development, platform-integration | defi-protocols, security-analysis |
| **NFT Automation** | agent-development, graph-development | nft, wallet |
| **DAO Governance Bot** | agent-development, testing-patterns | dao-tooling, identity-auth |
| **Security Analyzer** | tool-development | security-analysis, onchain-analysis |

## Vibe Coding with SpoonOS Skills

Copy **SpoonOS Skills** into your workspace to enable **vibe coding** - describe what you want and let AI generate production-ready SpoonOS agents:

### Quick Setup

```bash
# Step 1: Copy SpoonOS Skills for Vibe Coding (Claude Code / Cursor / Windsurf)
mkdir -p .claude/skills
cp -r spoonos-skills/* .claude/skills/

# Step 2: Copy Web3 Skills for your generated agents to use
mkdir -p .agent/skills
cp -r web3-skills/* .agent/skills/
```

### Just Describe What You Want

With SpoonOS skills installed, describe your goal and the AI generates complete agents:

| You Say | SpoonOS Skills Used | Generated Output |
|---------|---------------------|------------------|
| "Build a trading bot for Uniswap" | agent-development, application-templates | Complete `SpoonReactSkill` agent |
| "Create a DAO voting monitor" | agent-development, platform-integration | Agent with Telegram/Discord alerts |
| "Deploy my agent to AWS Lambda" | deployment-guide | Dockerfile + Lambda handler |
| "Add security checks to my bot" | tool-development | Agent that loads security-analysis skills |

### Example Vibe Coding Session

```
You: "I want an agent that monitors Aave positions and alerts me on Telegram
     when my health factor drops below 1.5"

Claude Code: Using SpoonOS skills: agent-development, platform-integration

[Generates complete SpoonReactSkill agent that:]
- Loads Web3 skills from .agent/skills/
- Uses defi-protocols/scripts/aave_lending.py as a tool
- Integrates platform-integration/scripts/telegram_bot.py
- Runs on a schedule via platform-integration/scripts/scheduler.py
```

## Collections

### SpoonOS Skills (8 skills, 21 scripts) — For Vibe Coding

**Empower developers to build SpoonOS Agents and applications.**

Copy these skills to `.claude/skills/` and use Vibe Coding to generate complete agents.

| Skill | Description | Scripts |
|-------|-------------|---------|
| [Agent Development](./spoonos-skills/agent-development/) | Build AI agents with SpoonReactMCP/SpoonReactSkill | 3 |
| [Graph Development](./spoonos-skills/graph-development/) | StateGraph workflow construction | 2 |
| [ERC-8004 Standard](./spoonos-skills/erc8004-standard/) | Trustless on-chain agent identity | 1 |
| [Tool Development](./spoonos-skills/tool-development/) | MCP tools and toolkit extensions | 2 |
| [Application Templates](./spoonos-skills/application-templates/) | Trading bot, NFT minter, DAO assistant | 3 |
| [Platform Integration](./spoonos-skills/platform-integration/) | Telegram, Discord, REST API, Scheduler | 4 |
| [Deployment Guide](./spoonos-skills/deployment-guide/) | Docker, AWS Lambda, Cloud Run | 3 |
| [Testing Patterns](./spoonos-skills/testing-patterns/) | Unit tests, LLM mocking, graph tests | 3 |

[View SpoonOS Skills Documentation →](./spoonos-skills/README.md)

### Web3 Skills (11 skills, 36 scripts) — For Skill Agent Integrations

**Provide blockchain tools for `SpoonReactSkill` agents to use.**

Copy these skills to `.agent/skills/` and your skill agents will automatically load them as tools.

| Skill | Description | Chains | Scripts |
|-------|-------------|--------|---------|
| [DeFi Protocol](./web3-skills/defi/) | Uniswap, Aave, TVL tracking | EVM | 3 |
| [DeFi Protocols (Advanced)](./web3-skills/defi-protocols/) | Aave V3, 1inch, CoW Protocol, Yield | EVM | 4 |
| [NFT Market](./web3-skills/nft/) | OpenSea, rarity, trends | EVM, Solana | 3 |
| [On-Chain Analysis](./web3-skills/onchain-analysis/) | Etherscan, gas, contracts | EVM | 4 |
| [Wallet Operations](./web3-skills/wallet/) | Balance, portfolio, tx builder | Multi-chain | 3 |
| [Cross-Chain Bridge](./web3-skills/bridge/) | Quote, routes, status | Multi-chain | 3 |
| [Solana Ecosystem](./web3-skills/solana/) | Jupiter, balance, NFT | Solana | 3 |
| [Neo Ecosystem](./web3-skills/neo/) | Balance, contracts | Neo | 2 |
| [Identity & Auth](./web3-skills/identity-auth/) | SIWE, ENS, sessions | EVM | 3 |
| [Security Analysis](./web3-skills/security-analysis/) | GoPlus, Honeypot, Flashbots | EVM | 4 |
| [DAO Tooling](./web3-skills/dao-tooling/) | Snapshot, Tally, Governor | EVM | 4 |

[View Web3 Skills Documentation →](./web3-skills/README.md)

## Example: Building a Web3 Skill Agent

Use `SpoonReactSkill` to build agents that automatically load and use Web3 skills:

```python
from spoon_ai.agents import SpoonReactSkill
from spoon_ai.chat import ChatBot

# Path to your skills directory
SKILLS_PATH = ".claude/skills"  # or ".agent/skills"

class DeFiSkillAgent(SpoonReactSkill):
    """
    A DeFi agent that automatically activates Web3 skills.
    Skills provide both prompts AND executable scripts as tools.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'defi_skill_agent')
        kwargs.setdefault('description', 'AI agent for DeFi operations')
        kwargs.setdefault('skill_paths', [SKILLS_PATH])
        kwargs.setdefault('scripts_enabled', True)  # Enable script execution
        kwargs.setdefault('max_steps', 10)

        super().__init__(**kwargs)

    async def initialize(self):
        await super().initialize()

        # Activate Web3 skills - scripts become tools automatically
        available_skills = self.list_skills()
        print(f"Available skills: {available_skills}")

        # Activate relevant skills
        if "defi-protocols" in available_skills:
            await self.activate_skill("defi-protocols")
        if "security-analysis" in available_skills:
            await self.activate_skill("security-analysis")

        # Show active tools from skills
        tools = self.skill_manager.get_active_tools()
        print(f"Active tools: {[t.name for t in tools]}")


async def main():
    # Create agent with skill system
    agent = DeFiSkillAgent(
        llm=ChatBot(llm_provider="openai", model_name="gpt-4o"),
        auto_trigger_skills=True,  # Auto-activate matching skills
        max_auto_skills=3
    )

    await agent.initialize()

    # Agent uses skill scripts as tools
    result = await agent.run(
        "Check if PEPE token is safe, then find the best swap route for 1 ETH to USDC"
    )
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### How It Works

1. **Skill Paths**: Agent loads skills from `.claude/skills/` or `.agent/skills/`
2. **Scripts as Tools**: Python scripts in `scripts/` become callable tools
3. **Auto-Activation**: Skills matching the query activate automatically
4. **Skill Prompts**: SKILL.md content enhances the agent's system prompt

## Skill Format

Each skill follows a standardized format:

```
skill-name/
├── SKILL.md              # Skill definition with YAML frontmatter
├── scripts/              # Python scripts (runnable code)
│   └── script_name.py
└── references/           # Reference documentation
    └── reference.md
```

### SKILL.md Structure

```yaml
---
name: skill-name
description: Brief description for triggering
---

# Skill Title

## Quick Start
[Minimal code example]

## Scripts
[Link to scripts]

## References
[Link to references]

## Best Practices
[Guidelines]
```

## Installation

### Option 1: Workspace Skills (Recommended for Vibe Coding)

```bash
# Clone the repository
git clone https://github.com/XSpoonAi/spoon-awesome-skill.git

# Copy to your project's skill directory
mkdir -p your-project/.claude/skills
cp -r spoon-awesome-skill/spoonos-skills/* your-project/.claude/skills/
cp -r spoon-awesome-skill/web3-skills/* your-project/.claude/skills/
```

### Option 2: Global Skills

```bash
# Copy to global Claude Code skills directory
cp -r spoon-awesome-skill/spoonos-skills/* ~/.claude/skills/
cp -r spoon-awesome-skill/web3-skills/* ~/.claude/skills/
```

### Option 3: Direct Import

```python
# Import scripts directly in your code
from spoon_awesome_skill.web3_skills.defi.scripts.uniswap_quote import UniswapQuoteTool
```

## Environment Variables

Create a `.env` file with the required API keys:

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Blockchain RPCs
ETHEREUM_RPC=https://eth.llamarpc.com
POLYGON_RPC=https://polygon.llamarpc.com
ARBITRUM_RPC=https://arb1.arbitrum.io/rpc
BASE_RPC=https://mainnet.base.org

# Web3 APIs
ETHERSCAN_API_KEY=...
ALCHEMY_API_KEY=...

# DeFi (Optional)
ONEINCH_API_KEY=...
TENDERLY_API_KEY=...

# Wallet (For transactions)
PRIVATE_KEY=0x...
WALLET_ADDRESS=0x...
```

## Contributing

1. Fork the repository
2. Create a new skill following the format
3. Add scripts to `scripts/` directory
4. Update the collection README
5. Submit a pull request

## License

MIT License
