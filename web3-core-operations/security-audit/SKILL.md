---
name: security-audit
description: |
  Smart contract security audit assistant powered by Solodit API. Search 50,000+ vulnerabilities, fetch contracts from 40+ chains, run static analysis, generate PoC exploits and audit reports.
version: 1.0.0
author: OS-Lihua <os-lihua@users.noreply.github.com>
tags: [security, audit, vulnerability, solodit, slither, aderyn, exploit, poc, smart-contract]
---

# Security Audit Skill

Smart contract security audit assistant powered by Solodit API and professional audit tools.

## Quick Start

```bash
# Search vulnerabilities
python3 scripts/solodit_api.py search --keywords "reentrancy" --impact HIGH

# Fetch contract from Etherscan URL
python3 scripts/fetch_contract.py "https://etherscan.io/address/0x..."

# Detect project framework
python3 scripts/project_detector.py /path/to/project
```

## Scripts

| Script | Purpose |
|--------|---------|
| [solodit_api.py](scripts/solodit_api.py) | Search Solodit vulnerability database |
| [fetch_contract.py](scripts/fetch_contract.py) | Fetch verified contracts from 40+ chains |
| [project_detector.py](scripts/project_detector.py) | Detect project framework and chain type |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SOLODIT_API_KEY` | Yes | Solodit API key from https://solodit.cyfrin.io |
| `ETHERSCAN_API_KEY` | No | Etherscan API key for fetching contracts |
| `BSCSCAN_API_KEY` | No | BSCScan API key |
| `ARBISCAN_API_KEY` | No | Arbiscan API key |

## Capabilities

1. **Search Vulnerabilities** - Query 50,000+ findings from top audit firms (Cyfrin, Sherlock, Code4rena, etc.)
2. **Fetch Contracts** - Download verified source code from 40+ blockchain explorers
3. **Detect Frameworks** - Auto-detect project framework (Foundry, Hardhat, Anchor, etc.)
4. **Static Analysis** - Run Slither, Aderyn, Mythril for automated scanning
5. **Fuzz Testing** - Echidna, Medusa, Foundry for invariant testing
6. **PoC Generation** - Templates for reentrancy, flash loan, oracle manipulation exploits
7. **Report Generation** - Code4rena, Sherlock, Cyfrin style audit reports

## Best Practices

1. Always verify contract source before auditing
2. Use multiple static analysis tools for comprehensive coverage
3. Search Solodit for similar vulnerabilities in related protocols
4. Write PoC tests to confirm findings
5. Follow severity guidelines when rating issues
