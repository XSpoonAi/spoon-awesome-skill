# DeFi Safety Shield

A comprehensive, zero-configuration DeFi security monitoring toolkit for SpoonOS agents. Protects users from honeypots, rug pulls, phishing sites, risky approvals, and unstable protocols — all using **free APIs with no API keys required**.

## Why This Skill?

The Web3 ecosystem is rife with scams: honeypot tokens, phishing sites, unlimited approval exploits, and protocol rug pulls. DeFi Safety Shield is the **first monitoring skill in the AI Productivity track** that brings multi-source security intelligence to SpoonOS agents, enabling them to protect users before they make costly mistakes.

### What Makes It Different

| Feature | This Skill | Existing Security Skills |
|---------|-----------|------------------------|
| API Keys Required | **None** | Tenderly key, Private key |
| Configuration | **Zero setup** | Multiple env vars |
| Token Analysis | GoPlus + Honeypot.is | GoPlus only |
| Protocol Risk | DeFi Llama TVL/audit | Not available |
| Approval Auditing | GoPlus v2 | Not available |
| Phishing Detection | GoPlus + URL patterns | Not available |
| Multi-Chain | 9 chains | Limited |

## Quick Start

### For Vibe Coding (Claude Code / SpoonOS Skills)

```bash
cp -r defi-safety-shield/ .claude/skills/defi-safety-shield/
# Or: cp -r defi-safety-shield/ .agent/skills/defi-safety-shield/
```

### For SpoonReactSkill Agent

```python
from spoon_ai.agents import SpoonReactSkill

agent = SpoonReactSkill(
    name="security_monitor",
    skill_paths=["ai-productivity/monitoring/defi-safety-shield"],
    scripts_enabled=True
)
await agent.activate_skill("defi-safety-shield")
result = await agent.run("Is this token safe? 0xdAC17F958D2ee523a2206206994597C13D831ec7")
```

### Direct Script Execution

```bash
# Scan a token for honeypot/rug pull risks
echo '{"token_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "chain": "ethereum"}' | python3 scripts/token_risk_scanner.py

# Assess DeFi protocol risk
echo '{"protocol": "aave"}' | python3 scripts/protocol_risk_scorer.py

# Audit wallet approvals
echo '{"wallet_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "chain": "ethereum"}' | python3 scripts/wallet_approval_audit.py

# Check for phishing site
echo '{"url": "https://app.uniswap.org"}' | python3 scripts/phishing_detector.py
```

## Scripts

| Script | Purpose | APIs Used |
|--------|---------|-----------|
| [token_risk_scanner.py](scripts/token_risk_scanner.py) | Honeypot, rug pull, tax, contract security | GoPlus + Honeypot.is |
| [protocol_risk_scorer.py](scripts/protocol_risk_scorer.py) | Protocol TVL, audit, hack risk assessment | DeFi Llama |
| [wallet_approval_audit.py](scripts/wallet_approval_audit.py) | Token approval risks, unlimited allowances | GoPlus v2 |
| [phishing_detector.py](scripts/phishing_detector.py) | Phishing URLs, dApp security verification | GoPlus |

## Detailed API Documentation

### token_risk_scanner.py

Combines GoPlus Security and Honeypot.is to provide deep token security analysis.

**Input:**
```json
{
  "token_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
  "chain": "ethereum"
}
```

**Output:**
```json
{
  "success": true,
  "scan_type": "token_risk",
  "token": {
    "name": "Tether USD",
    "symbol": "USDT",
    "chain": "ethereum"
  },
  "risk_assessment": {
    "score": 3,
    "level": "LOW",
    "critical_flags": [],
    "warnings": ["Token has blacklist function", "Token is mintable"],
    "info": ["Contract source code is verified", "Token is on GoPlus trusted list"]
  },
  "taxes": {
    "buy_tax_percent": 0.0,
    "sell_tax_percent": 0.0
  },
  "contract_security": {
    "is_open_source": true,
    "is_proxy": true,
    "is_mintable": true,
    "has_self_destruct": false,
    "hidden_owner": false,
    "transfer_pausable": true
  },
  "holder_analysis": {
    "total_holders": "5812342",
    "top_holders": [...],
    "creator_percent": 0.0
  },
  "liquidity": {
    "dex_listed": true,
    "dex": [{"name": "Uniswap V3", "liquidity": "123456789"}]
  },
  "honeypot_simulation": {
    "is_honeypot": false,
    "buy_tax_simulated": 0.0,
    "sell_tax_simulated": 0.0
  }
}
```

**Risk Checks Performed:**
- Honeypot detection (GoPlus + Honeypot.is double-check)
- Buy/sell tax analysis (flags >5%, warns >10%, critical >50%)
- Contract verification (open source, proxy, mintable)
- Ownership risks (hidden owner, reclaimable ownership, balance modification)
- Self-destruct capability
- Blacklist/whitelist functions
- Transfer pausability
- Slippage modification capability
- Holder concentration analysis
- Creator honeypot history
- Liquidity assessment

### protocol_risk_scorer.py

Assesses DeFi protocol risk using TVL, audit status, and metadata from DeFi Llama.

**Input:**
```json
{"protocol": "aave"}
```

**Output:**
```json
{
  "success": true,
  "scan_type": "protocol_risk",
  "protocol": {
    "name": "Aave",
    "category": "Lending",
    "url": "https://aave.com"
  },
  "tvl": {
    "current_usd": 26753741520,
    "change_1d_percent": -1.5,
    "change_7d_percent": 3.2,
    "chain_breakdown": {
      "Ethereum": 15000000000,
      "Polygon": 1200000000
    }
  },
  "metadata": {
    "chains": ["Ethereum", "Polygon", "Avalanche"],
    "chain_count": 10,
    "audits": "2",
    "forked_from": [],
    "oracles": ["Chainlink"]
  },
  "risk_assessment": {
    "score": 1,
    "level": "SAFE",
    "factors": [
      {"factor": "Strong TVL", "detail": "TVL is $26,753,741,520", "impact": "0 (positive signal)"},
      {"factor": "Audited", "detail": "Audit status: 2", "impact": "0 (positive signal)"},
      {"factor": "Multi-chain presence", "detail": "Deployed on 10 chains", "impact": "0 (positive signal)"}
    ]
  }
}
```

**Risk Factors Assessed:**
- TVL size (<$100K = critical, <$1M = high, <$10M = medium)
- TVL trend 24h (>20% drop = severe, >10% = major, >5% = notable)
- TVL trend 7d (>30% drop = severe, >15% = decline)
- Audit status (unaudited = +2 risk)
- Chain diversity (single chain = +1 risk)
- Fork status (forked = +1 risk)
- Protocol age (<30 days = +2, <90 days = +1)

### wallet_approval_audit.py

Audits ERC-20 token approvals for a wallet using GoPlus v2 API.

**Input:**
```json
{
  "wallet_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "chain": "ethereum"
}
```

**Output:**
```json
{
  "success": true,
  "scan_type": "wallet_approval_audit",
  "wallet": {
    "address": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
    "chain": "ethereum"
  },
  "address_security": {
    "flags": null,
    "is_contract": false
  },
  "risk_assessment": {
    "score": 2,
    "level": "LOW"
  },
  "approval_analysis": {
    "total_approvals": 15,
    "unlimited_approvals": 3,
    "risky_approvals": 0,
    "malicious_spenders": 0,
    "approvals": [...]
  },
  "recommendations": [
    "Revoke or reduce 3 unlimited approval(s)"
  ]
}
```

**Checks Performed:**
- Wallet address security flags (phishing, cybercrime, money laundering)
- All active ERC-20 token approvals
- Unlimited approval detection
- Spender contract verification (open source, malicious behavior)
- Spender trust/doubt list status
- Recommendations for which approvals to revoke

### phishing_detector.py

Detects phishing URLs and verifies dApp security using GoPlus and URL pattern analysis.

**Input:**
```json
{
  "url": "https://app.uniswap.org",
  "check_type": "both"
}
```

**Output:**
```json
{
  "success": true,
  "scan_type": "phishing_detection",
  "target_url": "https://app.uniswap.org",
  "domain": "app.uniswap.org",
  "url_pattern_analysis": {
    "warnings": null,
    "suspicious_patterns_found": 0
  },
  "phishing_check": {
    "is_phishing": false,
    "source": "GoPlus Security Database"
  },
  "dapp_security": {
    "available": true,
    "project_name": "Uniswap",
    "is_audited": true,
    "is_trusted": true,
    "audits": [{"firm": "Trail of Bits", "link": "..."}],
    "contracts": [...]
  },
  "risk_assessment": {
    "score": 0,
    "level": "SAFE",
    "verdicts": ["dApp is on GoPlus trusted list", "dApp has been audited"]
  }
}
```

**Check types:**
- `"phishing"` — Only GoPlus phishing database check
- `"dapp"` — Only dApp security verification
- `"both"` — Full phishing + dApp analysis (default)

**Detection Methods:**
- GoPlus phishing site database
- URL pattern analysis (suspicious TLDs, typosquatting, IP-based URLs)
- dApp audit verification
- Associated smart contract maliciousness check
- Trust list verification

## Risk Scoring System

All tools use a unified 0-10 risk scoring system:

| Level | Score | Color | Action |
|-------|-------|-------|--------|
| SAFE | 0-1 | Green | No risks detected |
| LOW | 2-3 | Yellow | Minor concerns, generally safe |
| MEDIUM | 4-5 | Orange | Proceed with caution |
| HIGH | 6-7 | Red | Not recommended |
| CRITICAL | 8-10 | Red | Likely scam/exploit — avoid |

## Supported Chains

| Chain | ID | Token Scan | Approval Audit | Phishing |
|-------|----|-----------|----------------|----------|
| Ethereum | 1 | Yes | Yes | Yes |
| BSC | 56 | Yes | Yes | Yes |
| Polygon | 137 | Yes | Yes | Yes |
| Arbitrum | 42161 | Yes | Yes | Yes |
| Base | 8453 | Yes | Yes | Yes |
| Optimism | 10 | Yes | Yes | Yes |
| Avalanche | 43114 | Yes | Yes | Yes |
| Linea | 59144 | Yes | Yes | Yes |
| zkSync Era | 324 | Yes | Yes | Yes |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| *(none)* | — | **No environment variables needed** |

All APIs used are free and require no authentication.

## Error Handling

All scripts return structured error responses:

```json
{"error": "Invalid address format: xyz. Expected 0x followed by 40 hex characters."}
{"error": "Rate limit exceeded. Please wait 1-2 minutes before retrying."}
{"error": "Token not found on chain 1. Verify the address and chain are correct."}
{"error": "Protocol not found: xyz. Check the name on defillama.com."}
```

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid address | Wrong format | Use 0x + 40 hex chars |
| Rate limit | Too many requests | Wait 1-2 minutes |
| Token not found | Wrong address/chain | Verify on block explorer |
| Protocol not found | Wrong name | Check defillama.com |
| Connection failed | Network issues | Check internet |

## Security Design

This skill follows strict security principles:

1. **Read-Only** — NEVER sends transactions, signs messages, or modifies blockchain state
2. **No Keys Required** — Zero API keys, zero private keys, zero wallet connections
3. **No Data Storage** — No user data persisted beyond the API call
4. **Input Validation** — Regex validation on all addresses, URL parsing on all links
5. **Safe Errors** — No stack traces or internal details in error messages
6. **Multi-Source** — Cross-references GoPlus, Honeypot.is, and DeFi Llama for accuracy
7. **Conservative** — Flags suspicious patterns even when unconfirmed (false positives > false negatives)

## Use Cases

1. **Before buying a token** — Scan for honeypot, taxes, and contract risks
2. **Before connecting to a dApp** — Verify it's not a phishing site
3. **Monthly security audit** — Check wallet approvals for stale/risky allowances
4. **Protocol due diligence** — Assess DeFi protocol stability before depositing
5. **Community protection** — Agents can proactively warn users about risky interactions

## Composability

This skill composes well with other SpoonOS skills:

- **+ Market Intelligence**: Check token safety before trading based on price signals
- **+ On-Chain Analysis**: Combine security scan with transaction/wallet analysis
- **+ DeFi Skills**: Verify protocol safety before executing swaps/deposits
- **+ Bridge Skills**: Check token security on destination chain before bridging

## License

MIT License
