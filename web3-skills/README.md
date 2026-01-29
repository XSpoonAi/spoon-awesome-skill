# Web3 Skills Collection

A comprehensive collection of Web3-related Claude Code skills for blockchain development, DeFi interactions, NFT analysis, on-chain data, and cross-chain operations.

## Overview

This collection provides Claude Code with specialized capabilities for Web3 tasks:

| Category | Skills | Description |
|----------|--------|-------------|
| **DeFi** | defi-protocol-interaction | Uniswap, Aave, Compound interactions |
| **NFT** | nft-market-analysis | OpenSea, Blur, Magic Eden data |
| **On-Chain** | onchain-data-analysis | Etherscan, Dune Analytics queries |
| **Wallet** | wallet-operations | Balance queries, transaction building |
| **Bridge** | cross-chain-bridge | LayerZero, Wormhole, Stargate, Across |
| **Solana** | solana-ecosystem | Jupiter, Raydium, Magic Eden |
| **Neo** | neo-ecosystem | Neo N3, NeoX, NeoFS, NEP-17/NEP-11 |
| **DeFi Protocols** | advanced-defi | Aave V3, 1inch, CoW Protocol integrations |
| **Identity** | identity-auth | SIWE, ENS resolution, session management |
| **Security** | security-analysis | GoPlus, Honeypot detection, MEV protection |
| **DAO** | dao-tooling | Snapshot, Tally, Governor voting automation |
| **Gas** | gas-optimization | Base fee prediction, batch vs separate, EIP-1559, EIP-4844 blob |

## Directory Structure

```
web3-skills/
├── README.md                 # This file
├── defi/
│   ├── SKILL.md             # DeFi protocol interaction skill
│   └── scripts/
│       ├── uniswap_quote.py    # Uniswap V3 swap quotes
│       ├── aave_positions.py   # Aave lending positions
│       └── defi_tvl.py         # DeFi Llama TVL data
├── nft/
│   ├── SKILL.md             # NFT market analysis skill
│   └── scripts/
│       ├── opensea_collection.py  # OpenSea collection data
│       ├── nft_rarity.py          # Rarity calculations
│       └── market_trends.py       # NFT market trends
├── onchain-analysis/
│   ├── SKILL.md             # On-chain data analysis skill
│   └── scripts/
│       ├── etherscan_address.py    # Address analysis
│       ├── etherscan_transaction.py # Transaction analysis
│       ├── gas_tracker.py          # Gas price tracking
│       └── contract_analyzer.py    # Smart contract analysis
├── wallet/
│   ├── SKILL.md             # Wallet operations skill
│   └── scripts/
│       ├── wallet_balance.py     # Multi-token balance
│       ├── portfolio_tracker.py  # Portfolio tracking
│       └── tx_builder.py         # Transaction construction
├── bridge/
│   ├── SKILL.md             # Cross-chain bridge skill
│   └── scripts/
│       ├── bridge_quote.py     # Bridge quotes
│       ├── bridge_routes.py    # Route optimization
│       └── bridge_status.py    # Status tracking
├── solana/
│   ├── SKILL.md             # Solana ecosystem skill
│   └── scripts/
│       ├── solana_balance.py   # SOL/SPL balances
│       ├── jupiter_quote.py    # Jupiter swap quotes
│       └── solana_nft.py       # Solana NFT data
├── neo/
│   ├── SKILL.md             # Neo N3 ecosystem skill
│   └── scripts/
│       ├── neo_balance.py      # NEO/GAS balances
│       ├── neo_transfer.py     # NEP-17 transfers
│       └── neo_contract.py     # Contract interactions
├── defi-protocols/
│   ├── SKILL.md             # Advanced DeFi protocol integrations
│   └── scripts/
│       ├── aave_lending.py     # Aave V3 lending
│       ├── oneinch_swap.py     # 1inch aggregator
│       └── cow_swap.py         # CoW Protocol swaps
├── identity-auth/
│   ├── SKILL.md             # Web3 identity & authentication
│   └── scripts/
│       ├── siwe_auth.py        # Sign-In with Ethereum
│       ├── ens_resolver.py     # ENS resolution
│       └── session_manager.py  # Web3 sessions
├── security-analysis/
│   ├── SKILL.md             # Security analysis tools
│   └── scripts/
│       ├── goplus_security.py  # GoPlus token security
│       ├── honeypot_check.py   # Honeypot detection
│       └── tenderly_simulate.py # Transaction simulation
├── dao-tooling/
│   ├── SKILL.md             # DAO governance automation
│   └── scripts/
│       ├── snapshot_monitor.py  # Snapshot proposals
│       ├── snapshot_vote.py     # Snapshot voting
│       └── governor_vote.py     # On-chain voting
└── gas-optimization/
    ├── SKILL.md             # Gas optimization (when/how to send cheaper)
    ├── README.md
    └── scripts/
        ├── common.py            # Shared config and RPC helpers
        ├── base_fee_predict.py  # Base fee history, when-to-send
        ├── batch_quote.py       # Batch vs separate gas
        ├── estimate_optimize.py # eth_estimateGas + EIP-1559
        ├── blob_quote.py        # EIP-4844 blob (Ethereum)
        └── optimization_report.py # All-in-one report
```

## Quick Start

### Prerequisites

Set up the following environment variables:

```bash
# EVM Chains
export ETHERSCAN_API_KEY="your_key"
export RPC_URL="https://eth.llamarpc.com"

# Optional for specific chains
export POLYGON_RPC_URL="https://polygon-rpc.com"
export ARBITRUM_RPC_URL="https://arb1.arbitrum.io/rpc"

# NFT APIs
export OPENSEA_API_KEY="your_key"  # Optional

# Solana
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"
```

### Python Dependencies

```bash
pip install web3 requests
```

## Skills Overview

### DeFi Protocol Interaction

**Trigger Keywords:** uniswap, aave, compound, swap, lending, borrowing, liquidity, yield, defi

**Capabilities:**
- Get swap quotes from Uniswap V3
- Query Aave lending/borrowing positions
- Fetch TVL and APY data from DeFi Llama
- Compare rates across protocols

**Example Usage:**
```
"Get a quote to swap 1 ETH for USDC on Uniswap"
"Check my Aave position health factor for address 0x..."
"What's the current TVL of Aave?"
```

### NFT Market Analysis

**Trigger Keywords:** nft, opensea, blur, collection, floor price, rarity

**Capabilities:**
- Fetch collection stats from OpenSea
- Calculate NFT rarity scores
- Track market trends and volume
- Compare marketplace data

**Example Usage:**
```
"Get floor price for Bored Ape Yacht Club"
"Analyze rarity of BAYC #1234"
"Show trending NFT collections today"
```

### On-Chain Data Analysis

**Trigger Keywords:** etherscan, transaction, whale, gas, smart contract

**Capabilities:**
- Analyze wallet addresses
- Decode transaction details
- Track gas prices
- Audit smart contracts

**Example Usage:**
```
"Analyze this address: 0x..."
"Check transaction details for 0x..."
"What's the current gas price?"
```

### Wallet Operations

**Trigger Keywords:** wallet, balance, portfolio, transfer, send

**Capabilities:**
- Check multi-chain balances
- Track portfolio value
- Build transactions
- Estimate gas costs

**Example Usage:**
```
"Check my wallet balance on Ethereum"
"Show my portfolio across all chains"
"Build a transaction to send 1 ETH to 0x..."
```

### Cross-Chain Bridge

**Trigger Keywords:** bridge, cross-chain, layerzero, wormhole, stargate

**Capabilities:**
- Get quotes from multiple bridges
- Find optimal bridging routes
- Track bridge transaction status
- Compare fees and speeds

**Example Usage:**
```
"Bridge 1000 USDC from Ethereum to Arbitrum"
"Compare bridge options for ETH to Polygon"
"Check status of my Stargate bridge transaction"
```

### Solana Ecosystem

**Trigger Keywords:** solana, sol, jupiter, raydium, magic eden

**Capabilities:**
- Check SOL and SPL token balances
- Get Jupiter swap quotes
- Query Solana NFT collections
- Analyze staking positions

**Example Usage:**
```
"Check my Solana wallet balance"
"Get a quote to swap 10 SOL for USDC"
"What's the floor price of Mad Lads?"
```

### Neo Ecosystem

**Trigger Keywords:** neo, neo n3, gas, nep17, nep11, neox, neofs

**Capabilities:**
- Check NEO/GAS balances
- Build NEP-17 token transfers
- Query Neo N3 smart contracts
- Interact with NeoX EVM sidechain
- NeoFS decentralized storage

**Example Usage:**
```
"Check my NEO balance for address N..."
"Transfer 10 GAS to address N..."
"Query the NEO total supply"
"Get contract info for NeoToken"
```

## Supported Chains

### EVM Chains

| Chain | Chain ID | Native Token | Notes |
|-------|----------|--------------|-------|
| Ethereum | 1 | ETH | Mainnet |
| Polygon | 137 | POL | Renamed from MATIC (Sept 2024) |
| Arbitrum | 42161 | ETH | L2 Rollup |
| Optimism | 10 | ETH | L2 Rollup |
| Base | 8453 | ETH | Coinbase L2 |
| BSC | 56 | BNB | Binance Smart Chain |
| Avalanche | 43114 | AVAX | C-Chain |
| zkSync Era | 324 | ETH | ZK Rollup |
| Linea | 59144 | ETH | Consensys zkEVM |
| NeoX | 47763 | GAS | Neo EVM sidechain |

### Non-EVM Chains

| Chain | Native Token | Notes |
|-------|--------------|-------|
| Solana | SOL | High-performance L1 |
| Neo N3 | NEO/GAS | dBFT consensus |

## API References

### DeFi APIs
- [DeFi Llama API](https://api.llama.fi) - TVL and yields data
- [Uniswap Docs](https://docs.uniswap.org/) - DEX contracts
- [Aave Docs](https://docs.aave.com/) - Lending protocol

### NFT APIs
- [OpenSea API V2](https://api.opensea.io/api/v2/) - NFT marketplace (API key required)
- [Magic Eden API](https://api-mainnet.magiceden.dev/v2) - Solana/EVM NFTs

### On-Chain APIs
- [Etherscan API V2](https://api.etherscan.io/v2/api) - Block explorer (use `?chainid=X`)
- **Note:** Etherscan V1 API deprecated August 2025

### Bridge APIs
- [Stargate API](https://stargate.finance/api/v1) - 89 chains, LayerZero V2
- [Wormhole API](https://api.wormholescan.io/api/v1) - 50+ chains
- [Across API](https://app.across.to/api) - 21+ chains including Solana
- [LayerZero](https://metadata.layerzero-api.com/v1) - 80+ chains

### Solana APIs
- [Solana JSON-RPC](https://solana.com/docs/rpc)
- [Solscan Pro API](https://pro-api.solscan.io/v2.0/)
- [Jupiter API](https://station.jup.ag/docs/apis)

### Neo APIs
- [Neo RPC](https://mainnet1.neo.coz.io:443) - Neo N3 mainnet
- [Neo Mamba SDK](https://dojo.coz.io/neo3/mamba) - Python SDK
- [NeoX RPC](https://mainnet-1.rpc.banelabs.org) - EVM sidechain

## Security Best Practices

1. **Never share private keys** - All operations are read-only or transaction-building only
2. **Verify contract addresses** - Always verify before interacting
3. **Check approvals** - Review token approvals regularly
4. **Use hardware wallets** - For significant holdings
5. **Start small** - Test with small amounts first

## Contributing

Contributions are welcome! Please:

1. Follow the existing skill format
2. Include comprehensive SKILL.md documentation
3. Add working scripts with error handling
4. Test with real API calls
5. Update this README

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- [Solana Foundation](https://github.com/solana-foundation/solana-dev-skill) - Reference for Solana skill structure
- [ComposioHQ](https://github.com/ComposioHQ/awesome-claude-skills) - Inspiration for skill organization
- [UCAI](https://github.com/nirholas/UCAI) - ABI-to-MCP patterns
- [EVM MCP Tools](https://github.com/0xGval/evm-mcp-tools) - EVM analysis patterns
