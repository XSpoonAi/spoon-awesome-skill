# whale-tracker

Track and analyze large wallet holders (whales) with real blockchain RPC data, ERC20 transfer monitoring, and behavior classification.

## Overview

This skill analyzes and tracks whale wallet activity using real blockchain RPC endpoints and transfer event monitoring. It fetches balance data, monitors ERC20 token transfers, classifies whale behavior patterns (accumulating/distributing/trading), detects exchange flows, and provides comprehensive analytics on wealth distribution and whale movement patterns.

## Features

- ✅ Real blockchain RPC integration (eth_getBalance, eth_getTransactionCount, eth_getLogs)
- ✅ ERC20 Transfer event monitoring for whale movements
- ✅ Whale behavior classification (accumulating, distributing, trading, holding)
- ✅ Exchange flow detection (whale-to-exchange deposit patterns)
- ✅ Multi-network support (Ethereum, Polygon)
- ✅ Whale categorization by balance size (Mega/Large/Medium)
- ✅ Activity level tracking (Active/Low Activity)
- ✅ Recent transfer detection
- ✅ Balance concentration analysis
- ✅ Transaction count per whale
- ✅ Whale ranking by holdings
- ✅ Behavior pattern analysis
- ✅ Portfolio statistics
- ✅ Dual-mode operation (API + Parameter)

## Usage

### API Mode with Transfer Tracking
```bash
python scripts/main.py --params '{"use_api": true, "network": "ethereum", "addresses": ["0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d", "0x7d8c9e4f3b2a1e0d5c6b7a8f9e0d1c2b3a4f5e6d"], "threshold_usd": 1000000}'
```

### Parameter Mode (Custom Whale Data)
```bash
python scripts/main.py --params '{"use_api": false, "network": "ethereum", "movements": [{"address": "0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d", "balance_eth": 100, "balance_usd": 200000, "behavior": "accumulating"}], "threshold_usd": 1000000}'
```

## Parameters

### API Mode Parameters
- `use_api` (boolean, required): Enable blockchain RPC integration with transfer tracking
- `network` (string, required): "ethereum" or "polygon"
- `addresses` (array, required): Wallet addresses to analyze (up to 50 per request)
- `threshold_usd` (number, required): Minimum balance to classify as whale

### Parameter Mode Parameters
- `use_api` (boolean, required): Disable API (false)
- `network` (string, required): Network identifier
- `movements` (array, required): Array of wallet objects with:
  - `address`: Wallet address
  - `balance_eth`: ETH balance
  - `balance_usd`: USD equivalent balance
  - `transaction_count`: Number of transactions
  - `behavior`: Whale behavior pattern (optional)
- `threshold_usd` (number, required): Minimum balance threshold

## Output

Returns JSON with:
- `status`: "success" or "error"
- `source`: "blockchain_api_with_transfers" or "parameters"
- `network`: Analyzed network
- `whale_count`: Total whales above threshold
- `whale_categories`: Breakdown by size (Mega/Large/Medium)
- `total_whale_volume_usd`: Combined holdings
- `avg_whale_balance_usd`: Average holdings per whale
- `activity_summary`: Distribution of activity levels
- `behavior_analysis`: Distribution of behavior patterns
- `top_whales`: List of top 20 whales with details including behavior
- `concentration_ratio`: Percentage held by largest whale
- `total_tx_count`: All transactions across whales
- `total_recent_transfers`: Count of recent ERC20 transfers
- `whale_movements`: Behavioral mapping with transfer counts
- `whale_addresses`: Array of top whale addresses

## Whale Classification

### By Balance Size
- **Mega Whales**: > $50M in holdings
- **Large Whales**: $10M - $50M
- **Medium Whales**: $1M - $10M

### By Activity
- **Active**: > 100 transactions (regular trader)
- **Low Activity**: ≤ 100 transactions (HODLer)

### By Behavior Pattern
- **Accumulating**: More inflows from exchanges (buying/receiving tokens)
- **Distributing**: More outflows to exchanges (selling/sending tokens)
- **Trading**: Mixed transfer patterns (active trading activity)
- **Holding**: No recent token transfers (static balances)

## Whale Movement Signals

The analyzer detects:
- **Whale → Exchange Flow**: Potential sell signal
- **Exchange → Whale Flow**: Potential accumulation signal
- **Recent Token Transfers**: Activity indicators
- **Transfer Frequency**: Engagement and trading velocity
- **Behavior Transitions**: Pattern changes over time

## Concentration Metrics

- **Concentration Ratio**: Top whale's share of total holdings
  - > 50%: Extreme concentration
  - 20-50%: High concentration
  - 10-20%: Moderate concentration
  - < 10%: Distributed holdings

## Examples

### Analyze Top Ethereum Whales with Transfer Tracking (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "ethereum",
  "addresses": [
    "0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d",
    "0x7d8c9e4f3b2a1e0d5c6b7a8f9e0d1c2b3a4f5e6d",
    "0xfe1da48c2e0d3b5a1c7f9e2d4a6b8c0e1f3d5a7c"
  ],
  "threshold_usd": 1000000
}'
```

### Analyze Polygon Whales (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "polygon",
  "addresses": ["0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d"],
  "threshold_usd": 500000
}'
```

### Analyze Custom Whale Portfolio with Behavior (Parameter Mode)
```bash
python scripts/main.py --params '{
  "use_api": false,
  "network": "ethereum",
  "movements": [
    {
      "address": "0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d",
      "balance_eth": 200,
      "balance_usd": 400000000,
      "transaction_count": 8500,
      "activity_level": "active",
      "behavior": "accumulating",
      "recent_transfers": 7
    },
    {
      "address": "0x7d8c9e4f3b2a1e0d5c6b7a8f9e0d1c2b3a4f5e6d",
      "balance_eth": 75,
      "balance_usd": 150000000,
      "transaction_count": 4500,
      "activity_level": "active",
      "behavior": "distributing",
      "recent_transfers": 4
    }
  ],
  "threshold_usd": 1000000
}'
```

## Key Insights

- **Portfolio Concentration**: Higher ratio = more wealth held by few whales
- **Behavior Patterns**: 
  - Accumulating whales indicate potential buying pressure
  - Distributing whales may signal selling pressure
  - Trading whales show high engagement
- **Activity Patterns**: Active whales more likely to trade
- **Transaction Count**: Indicator of engagement and trading frequency
- **Transfer Frequency**: Shows trading velocity and engagement level
- **Exchange Flows**: Detect major buy/sell movements

## Supported Networks

- Ethereum Mainnet
- Polygon

## Category

web3-data-intelligence
