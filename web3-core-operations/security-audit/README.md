# Security Audit Skill

A comprehensive smart contract security audit assistant powered by [Solodit API](https://solodit.cyfrin.io) and professional audit tools.

## Features

- **Vulnerability Search**: Query 50,000+ findings from top audit firms
- **Contract Fetching**: Download verified source from 40+ blockchain explorers
- **Framework Detection**: Auto-detect Foundry, Hardhat, Anchor, and 10+ frameworks
- **Static Analysis Integration**: Slither, Aderyn, Mythril, 4naly3er
- **Fuzz Testing**: Echidna, Medusa, Foundry, Halmos
- **PoC Templates**: Ready-to-use exploit templates
- **Report Generation**: Code4rena, Sherlock, Cyfrin style templates

## Installation

```bash
# Copy to your skills directory
cp -r security-audit/ .claude/skills/
# or
cp -r security-audit/ .agent/skills/
```

## Configuration

### Required Environment Variables

```bash
# Solodit API (required for vulnerability search)
export SOLODIT_API_KEY=sk_your_key_here
```

Get your API key at: https://solodit.cyfrin.io (Profile → API Keys)

### Optional Environment Variables

```bash
# Blockchain Explorers (for fetching contracts)
export ETHERSCAN_API_KEY=xxx
export BSCSCAN_API_KEY=xxx
export ARBISCAN_API_KEY=xxx
export POLYGONSCAN_API_KEY=xxx
export OPTIMISM_API_KEY=xxx
export BASESCAN_API_KEY=xxx
# ... and 30+ more chains supported

# RPC URLs (for fork testing)
export ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/xxx
```

## Scripts

### 1. solodit_api.py - Vulnerability Search

Search the Solodit database of 50,000+ smart contract vulnerabilities.

```bash
# Basic search
python3 scripts/solodit_api.py search --keywords "reentrancy"

# Filter by severity
python3 scripts/solodit_api.py search --keywords "flash loan" --impact HIGH

# Filter by audit firm
python3 scripts/solodit_api.py search --firms Cyfrin,Sherlock

# Filter by tags
python3 scripts/solodit_api.py search --tags "Oracle,Reentrancy"

# Filter by protocol category
python3 scripts/solodit_api.py search --category DeFi

# Recent findings
python3 scripts/solodit_api.py search --days 30 --limit 50

# Sort by quality
python3 scripts/solodit_api.py search --keywords "oracle" --sort Quality

# Output as JSON
python3 scripts/solodit_api.py search --keywords "price manipulation" --json
```

#### Search Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--keywords, -k` | Search text | `"reentrancy"` |
| `--impact, -i` | Severity levels | `HIGH,MEDIUM,LOW,GAS` |
| `--firms, -f` | Audit firms | `Cyfrin,Sherlock,Code4rena` |
| `--tags, -t` | Vulnerability tags | `Oracle,Reentrancy,Access Control` |
| `--protocol, -p` | Protocol name | `Uniswap` |
| `--category, -c` | Protocol category | `DeFi,NFT,Bridge` |
| `--languages, -l` | Languages | `Solidity,Rust,Move` |
| `--days, -d` | Recent days | `30`, `60`, `90` |
| `--quality` | Min quality score | `0-5` |
| `--rarity` | Min rarity score | `0-5` |
| `--sort` | Sort field | `Recency`, `Quality`, `Rarity` |
| `--order` | Sort order | `Desc`, `Asc` |
| `--page` | Page number | `1` |
| `--limit` | Results per page | `20` (max 100) |
| `--json` | Output raw JSON | flag |
| `--verbose, -v` | Show content preview | flag |

### 2. fetch_contract.py - Contract Fetcher

Fetch verified contract source code from 40+ blockchain explorers.

```bash
# Fetch from Etherscan URL
python3 scripts/fetch_contract.py "https://etherscan.io/address/0x1234..."

# Fetch by address with chain
python3 scripts/fetch_contract.py 0x1234... --chain ethereum

# Custom output directory
python3 scripts/fetch_contract.py 0x1234... -c polygon -o ./audit/contracts

# Output as JSON
python3 scripts/fetch_contract.py 0x1234... -c arbitrum --json

# List supported chains
python3 scripts/fetch_contract.py --list
```

#### Supported Chains

**EVM Chains (30+):**
- Ethereum, Goerli, Sepolia
- BSC, BSC Testnet
- Polygon, Polygon zkEVM
- Arbitrum, Arbitrum Nova
- Optimism, Base, Linea
- Avalanche, Fantom
- zkSync, Scroll, Mantle, Blast
- Celo, Gnosis, Moonbeam, Moonriver
- Cronos, Aurora, Metis, Boba, Kava
- Mode, Taiko

**Non-EVM Chains:**
- Solana
- TON
- Near
- Aptos
- Sui
- Starknet
- Tron
- Neo

### 3. project_detector.py - Framework Detection

Auto-detect smart contract project framework and chain type.

```bash
# Detect framework
python3 scripts/project_detector.py /path/to/project

# Output as JSON
python3 scripts/project_detector.py /path/to/project --json
```

#### Supported Frameworks

| Framework | Chain | Config File |
|-----------|-------|-------------|
| Foundry | EVM | `foundry.toml` |
| Hardhat | EVM | `hardhat.config.js/ts` |
| Anchor | Solana | `Anchor.toml` |
| Neo C# | Neo | `*.csproj` |
| Neo Python | Neo | `requirements.txt` |
| Blueprint | TON | `blueprint.config.ts` |
| Tact | TON | `tact.config.json` |
| Aptos | Move | `Move.toml` |
| Sui | Move | `Move.toml` |
| Starknet Foundry | Cairo | `Scarb.toml` |
| CosmWasm | CosmWasm | `Cargo.toml` |

## Workflows

### Complete Audit Workflow

```bash
# 1. Get contract source
python3 scripts/fetch_contract.py "https://etherscan.io/address/0x..."

# 2. Detect framework
python3 scripts/project_detector.py ./contracts/ContractName

# 3. Run static analysis
slither . --filter-paths "test|lib"
aderyn . -o aderyn-report.md

# 4. Search similar vulnerabilities
python3 scripts/solodit_api.py search --keywords "lending oracle" --impact HIGH

# 5. Run tests
forge test -vvv

# 6. Fuzz critical functions
forge test --fuzz-runs 10000

# 7. Generate report using templates in references/
```

### Search Similar Vulnerabilities

```bash
# For a lending protocol
python3 scripts/solodit_api.py search --keywords "lending" --category DeFi --impact HIGH

# For an oracle integration
python3 scripts/solodit_api.py search --tags Oracle --quality 3

# Recent high-severity findings
python3 scripts/solodit_api.py search --impact HIGH --days 30 --sort Quality
```

## References

The `references/` directory contains additional documentation:

### Audit Tools (`references/audit_tools.md`)
- Static analysis tools (Slither, Aderyn, Mythril, Solhint, 4naly3er)
- Fuzzing tools (Echidna, Medusa, Foundry Fuzz, Halmos)
- Transaction analysis (Phalcon, MetaSleuth, Tenderly)

### Report Templates (`references/report_templates/`)
- `code4rena.md` - Code4rena competition format
- `sherlock.md` - Sherlock platform format
- `cyfrin.md` - Cyfrin professional format
- `generic.md` - General audit report format
- `finding_template.md` - Individual finding template
- `severity_guide.md` - Severity classification guide

### PoC Templates (`references/poc_templates/`)
- `reentrancy.md` - Reentrancy attack PoC
- `flash_loan.md` - Flash loan attack PoC
- `oracle_manipulation.md` - Oracle manipulation PoC
- `access_control.md` - Access control bypass PoC
- `integer_overflow.md` - Integer overflow PoC
- `price_manipulation.md` - Price manipulation PoC

### Test Frameworks (`references/test_frameworks/`)
- `evm_foundry.md` - Foundry testing guide
- `evm_hardhat.md` - Hardhat testing guide
- `solana_anchor.md` - Anchor testing guide
- `neo.md` - Neo testing guide
- `ton.md` - TON testing guide
- `move.md` - Move testing guide
- `cairo.md` - Cairo testing guide
- `cosmwasm.md` - CosmWasm testing guide

### Solodit Filters (`references/filters.md`)
- Complete list of available search filters
- Audit firm names
- Vulnerability tags
- Protocol categories

## API Reference

### SoloditAPI Class

```python
from scripts.solodit_api import search_findings

# Search with filters
result = search_findings(
    keywords="reentrancy",
    impact=["HIGH", "MEDIUM"],
    firms=["Cyfrin", "Sherlock"],
    tags=["Reentrancy"],
    category=["DeFi"],
    days=30,
    quality_score=3,
    sort_field="Quality",
    page=1,
    page_size=50
)

# Result structure
{
    "findings": [...],
    "metadata": {
        "totalResults": 150,
        "currentPage": 1,
        "totalPages": 3
    },
    "rateLimit": {
        "limit": 100,
        "remaining": 99
    }
}
```

### ContractFetcher Class

```python
from scripts.fetch_contract import fetch_contract_source, detect_chain_from_url

# Auto-detect chain from URL
chain = detect_chain_from_url("https://etherscan.io/address/0x...")

# Fetch source
result = fetch_contract_source("ethereum", "0x1234...")

# Result structure
{
    "ContractName": "MyContract",
    "SourceCode": "...",
    "ABI": "...",
    "CompilerVersion": "v0.8.19",
    "OptimizationUsed": "1",
    "Proxy": "0",
    "Implementation": ""
}
```

### ProjectDetector Class

```python
from scripts.project_detector import detect_framework

# Detect framework
result = detect_framework("/path/to/project")

# Result structure
{
    "detected": True,
    "framework": "foundry",
    "chain": "evm",
    "chain_name": "EVM (Ethereum/BSC/Polygon/etc)",
    "languages": ["Solidity", "Vyper"],
    "test_cmd": "forge test",
    "build_cmd": "forge build",
    "extensions": [".sol"]
}
```

## Best Practices

1. **Always verify source** - Fetch and verify contract source before auditing
2. **Multiple tools** - Use multiple static analysis tools for comprehensive coverage
3. **Search similar** - Search Solodit for similar vulnerabilities in related protocols
4. **Write PoCs** - Confirm findings with proof-of-concept tests
5. **Severity guidelines** - Follow consistent severity classification
6. **Check proxies** - Always check for proxy patterns and fetch implementation contracts
7. **Framework-specific** - Use appropriate testing framework for the chain

## License

MIT License
