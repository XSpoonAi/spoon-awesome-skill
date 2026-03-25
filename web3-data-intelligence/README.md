# Web3 Data Intelligence Skills

**Track Focus:** The "Brain" of Web3 - On-chain analysis, indexing, and transforming raw blockchain data into actionable insights.

## Skills Overview

| Skill | Description | Scripts | Chain Support |
|-------|-------------|---------|---------------|
| [On-Chain Analysis](./onchain-analysis/) | Blockchain data analysis, transaction tracking, whale monitoring | 6 | Multi-chain |
| [Security Analysis](./security-analysis/) | Smart contract auditing, vulnerability detection, risk assessment | 4 | EVM |

**Total: 2 skills, 10 scripts**

## Track Description

Web3 Data Intelligence focuses on extracting meaning from blockchain data. This includes:

- **On-Chain Analytics**: Transaction patterns, wallet behavior, protocol metrics
- **Security Auditing**: Smart contract vulnerability detection and risk scoring
- **Data Indexing**: Efficient querying and aggregation of blockchain state
- **Insight Generation**: Converting raw data into actionable intelligence

## Use Cases

1. **Whale Tracking**: Monitor large wallet movements and predict market impact
2. **Protocol Health**: Analyze TVL, user activity, and protocol metrics
3. **Security Scanning**: Detect vulnerabilities before deployment
4. **Market Research**: Token distribution, holder analysis, liquidity depth

## Challenge Track: Web3 Data Intelligence

**Goal:** Build skills that transform raw blockchain data into valuable insights.

**Submission Ideas:**
- Token holder distribution analyzer
- DeFi protocol health dashboard
- MEV detection and analysis
- Cross-chain flow tracker
- Smart contract similarity detector

## Getting Started

```python
from spoon_ai.agents import SpoonReactSkill

agent = SpoonReactSkill(
    name="data_analyst",
    skill_paths=["./web3-data-intelligence"],
    scripts_enabled=True
)

# Activate on-chain analysis
await agent.activate_skill("onchain-analysis")

# Query: "Analyze the top 10 whale wallets holding USDC"
response = await agent.run("Analyze the top 10 whale wallets holding USDC")
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for submission guidelines.

**PR Requirements:**
- Screenshots showing data analysis output
- Demo with real blockchain data queries
- Clear documentation of data sources
