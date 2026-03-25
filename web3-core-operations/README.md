# Web3 Core Operations Skills

**Track Focus:** The "Engine Room" of Web3 - Smart contracts, protocol management, and blockchain infrastructure.

## Skills Overview

| Skill | Description | Scripts | Chain Support |
|-------|-------------|---------|---------------|
| [Bridge](./bridge/) | Cross-chain asset transfers and bridging | 3 | Multi-chain |
| [DAO Tooling](./dao-tooling/) | Governance, proposals, treasury management | 4 | EVM |
| [DeFi](./defi/) | Core DeFi operations (swap, lend, stake) | 5 | Multi-chain |
| [DeFi Protocols](./defi-protocols/) | Protocol-specific integrations | 4 | EVM |
| [Identity & Auth](./identity-auth/) | Web3 identity, ENS, authentication | 3 | EVM |
| [Neo](./neo/) | Neo N3 blockchain operations | 4 | Neo N3 |
| [NFT](./nft/) | NFT minting, trading, metadata | 4 | Multi-chain |
| [Solana](./solana/) | Solana-specific operations | 5 | Solana |
| [Wallet](./wallet/) | Wallet management and transactions | 5 | Multi-chain |

**Total: 9 skills, 37 scripts**

## Track Description

Web3 Core Operations covers the fundamental building blocks of blockchain interaction:

- **Protocol Interactions**: Direct smart contract calls and state management
- **Cross-Chain Operations**: Bridge assets and data between chains
- **DeFi Primitives**: Swap, lend, borrow, stake, yield farming
- **Identity & Access**: ENS, authentication, wallet management
- **Governance**: DAO proposals, voting, treasury operations

## Use Cases

1. **Automated Trading**: Execute swaps across DEXs with optimal routing
2. **Yield Optimization**: Manage positions across lending protocols
3. **DAO Operations**: Create proposals, vote, manage treasury
4. **NFT Management**: Mint, transfer, list NFTs programmatically
5. **Cross-Chain Transfers**: Bridge assets with gas optimization

## Challenge Track: Web3 Core Operations

**Goal:** Build skills that enable seamless blockchain protocol interactions.

**Submission Ideas:**
- Multi-DEX aggregator skill
- Automated yield farming optimizer
- DAO proposal automation
- NFT collection deployment tool
- Gas-optimized batch transaction executor

## Getting Started

```python
from spoon_ai.agents import SpoonReactSkill

agent = SpoonReactSkill(
    name="defi_operator",
    skill_paths=["./web3-core-operations"],
    scripts_enabled=True
)

# Activate DeFi skill
await agent.activate_skill("defi")

# Query: "Swap 100 USDC to ETH on Uniswap with 0.5% slippage"
response = await agent.run("Swap 100 USDC to ETH on Uniswap with 0.5% slippage")
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for submission guidelines.

**PR Requirements:**
- Screenshots showing protocol interaction
- Demo with testnet or mainnet transactions
- Security considerations documented
