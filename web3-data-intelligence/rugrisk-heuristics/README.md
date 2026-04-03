# rugrisk-heuristics

Comprehensive token rug pull risk analysis with heuristic-based assessment.

## Overview

This skill provides comprehensive risk assessment for tokens by analyzing multiple security indicators and contract patterns. Uses multi-factor heuristic scoring to identify red flags for rug pulls, honeypots, and scam tokens.

## Features

- ✅ **Multi-factor Risk Assessment**: Ownership, liquidity, tax, and distribution analysis
- ✅ **Contract Pattern Detection**: Identifies pausable functions, unlimited mint, blacklist
- ✅ **Holder Distribution Analysis**: Detects concentration risk
- ✅ **Tax Structure Evaluation**: Analyzes buy/sell taxes
- ✅ **Contract Verification Check**: Verifies Etherscan source code availability
- ✅ **Dual-mode Operation**: API mode (live analysis) + parameter mode (custom data)
- ✅ **Normalized Risk Scoring**: 0-100 scale for easy comparison
- ✅ **Actionable Recommendations**: Color-coded risk levels with guidance

## Usage

### Analyze Token with Heuristics
```bash
python scripts/main.py --params '{"token_address":"0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48","ownership_renounced":true,"liquidity_locked":true,"buy_tax":0,"sell_tax":0,"top_10_holder_percentage":10,"contract_verified":true}'
```

### Analyze Suspicious Token
```bash
python scripts/main.py --params '{"token_address":"0x...","ownership_renounced":false,"liquidity_locked":false,"buy_tax":20,"sell_tax":20,"top_10_holder_percentage":75,"contract_verified":false}'
```

## Parameters

- `token_address` (string, required): Ethereum contract address (0x...)
- `network` (string, optional): ethereum (default), polygon, etc.
- `use_api` (boolean, optional): Enable API mode for live analysis
- `ownership_renounced` (boolean): Has ownership been renounced?
- `liquidity_locked` (boolean): Is liquidity locked?
- `buy_tax` (number): Buy tax percentage (0-100)
- `sell_tax` (number): Sell tax percentage (0-100)
- `top_10_holder_percentage` (number): % held by top 10 holders
- `contract_verified` (boolean): Is code verified on Etherscan?
- `contract_abi` (object, optional): Contract ABI for pattern detection

## Output

Returns comprehensive risk analysis with:
- `risk_score`: Numeric 0-100 risk score
- `overall_risk`: Risk level (low/medium/high/critical)
- `recommendation`: Action guidance with emoji indicator
- `critical_flags`: Count of critical severity issues
- `high_severity_flags`: Count of high severity issues
- `findings`: Detailed array of each risk factor
  - Check name, severity level, description, risk weight
- `analysis_timestamp`: Time of analysis

## Examples

### USDC Analysis - Safe Token
```bash
python scripts/main.py --params '{"token_address":"0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48","ownership_renounced":true,"liquidity_locked":true,"buy_tax":0,"sell_tax":0,"top_10_holder_percentage":5,"contract_verified":true}'
```
Returns: `overall_risk: "low"`, `recommendation: "✅ LOW RISK"`

### Suspicious Token - Critical Risk
```bash
python scripts/main.py --params '{"token_address":"0x...","ownership_renounced":false,"liquidity_locked":false,"buy_tax":25,"sell_tax":25,"top_10_holder_percentage":85,"contract_verified":false}'
```
Returns: `overall_risk: "critical"`, `recommendation: "🛑 CRITICAL RISK - Avoid"`

## Risk Factors & Scoring

| Factor | Good | Caution | Bad |
|--------|------|---------|-----|
| **Ownership** | Renounced (0) | - | Active (15) |
| **Liquidity** | Locked (0) | - | Unlocked (20) |
| **Tax** | <5% | 5-15% | >15% |
| **Concentration** | <30% | 30-60% | >60% |
| **Verification** | Verified (0) | - | Unverified (10) |
| **Pausable Funcs** | None (0) | - | Present (20) |
| **Unlimited Mint** | No (0) | - | Yes (25) |

## Risk Levels

| Level | Score | Indicator | Action |
|-------|-------|-----------|--------|
| **CRITICAL** | 60+ | 🛑 | Avoid - extreme risk |
| **HIGH** | 40-59 | ⚠️ | Extreme caution required |
| **MEDIUM** | 20-39 | ⚡ | Investigate further |
| **LOW** | 0-19 | ✅ | Relatively safe |

## Track

web3-data-intelligence
