---
name: whale-tracker
track: web3-data-intelligence
version: 0.3.0
summary: Track whale wallets with RPC balance, ERC20 transfers, and behavior classification (accumulating/distributing/trading)
---

## Description

Tracks and analyzes whale wallet activity using real blockchain RPC data, ERC20 transfer event monitoring, and behavior classification. Monitors large ETH holders, analyzes balance distribution, detects exchange flows, classifies whale behavior patterns, and provides comprehensive activity metrics and concentration analysis.

## Features

- Real blockchain RPC integration (eth_getBalance, eth_getTransactionCount, eth_getLogs)
- ERC20 Transfer event monitoring for whale movements
- Whale behavior classification (accumulating, distributing, trading, holding)
- Exchange flow detection (whale-to-exchange deposit patterns)
- Multi-network support (Ethereum, Polygon)
- Whale categorization by balance size
- Activity level classification
- Recent transfer tracking
- Balance concentration analysis
- Transaction count tracking
- Behavior pattern analysis
- Whale ranking and statistics
- Dual-mode operation (API + Parameter)

## Inputs

### API Mode with Transfer Tracking
```json
{
  "use_api": true,
  "network": "ethereum",
  "addresses": ["0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d", "0x7d8c9e4f3b2a1e0d5c6b7a8f9e0d1c2b3a4f5e6d"],
  "threshold_usd": 1000000
}
```

### Parameter Mode
```json
{
  "use_api": false,
  "network": "ethereum",
  "movements": [
    {
      "address": "0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d",
      "balance_eth": 100,
      "balance_usd": 200000,
      "transaction_count": 250,
      "behavior": "accumulating"
    }
  ],
  "threshold_usd": 1000000
}
```

## Outputs

```json
{
  "ok": true,
  "data": {
    "status": "success",
    "source": "blockchain_api_with_transfers",
    "network": "ethereum",
    "threshold_usd": 1000000,
    "whale_count": 8,
    "whale_categories": {
      "mega_whales": 2,
      "large_whales": 3,
      "medium_whales": 3
    },
    "total_whale_volume_usd": 525000000,
    "avg_whale_balance_usd": 65625000,
    "activity_summary": {
      "active": 6,
      "low_activity": 2
    },
    "behavior_analysis": {
      "accumulating": 3,
      "distributing": 2,
      "trading": 2,
      "holding": 1
    },
    "top_whales": [
      {
        "address": "0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d",
        "balance_eth": 200,
        "balance_usd": 400000000,
        "transaction_count": 8500,
        "activity_level": "active",
        "behavior": "accumulating",
        "recent_transfers": 7,
        "token_activity": "recent",
        "last_transfer_block": 19285420
      }
    ],
    "total_tx_count": 31500,
    "avg_tx_per_whale": 3937.5,
    "total_recent_transfers": 42,
    "concentration_ratio": 76.19,
    "whale_movements": {
      "0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d": {
        "behavior": "accumulating",
        "transfers": 7
      }
    },
    "whale_addresses": ["0x9b1f7592e72945c3c4bfff3d0f2c3e4d5a6b7c8d"],
    "analysis_timestamp": "2026-02-07T09:30:00.000Z"
  }
}
```

## Parameters

### API Mode Parameters
- `use_api` (boolean, required): Enable blockchain RPC integration with transfer tracking
- `network` (string, required): "ethereum" or "polygon"
- `addresses` (array, required): Wallet addresses to analyze (max 50 per request)
- `threshold_usd` (number, required): Minimum balance to classify as whale

### Parameter Mode Parameters
- `use_api` (boolean, required): Disable API (false)
- `network` (string, required): Network identifier
- `movements` (array, required): Wallet data with balance, transaction counts, and behavior
- `threshold_usd` (number, required): Minimum balance threshold

## Whale Categories

- **Mega Whales**: > $50M balance
- **Large Whales**: $10M - $50M balance
- **Medium Whales**: $1M - $10M balance

## Activity Levels

- **Active**: > 100 transactions
- **Low Activity**: ≤ 100 transactions

## Whale Behavior Patterns

- **Accumulating**: More inflows from exchanges (potential buying pressure)
- **Distributing**: More outflows to exchanges (potential selling pressure)
- **Trading**: Mixed transfer patterns (high trading activity)
- **Holding**: No recent token transfers (static positions)

## Key Metrics

- **Whale Count**: Total whales above threshold
- **Total Whale Volume**: Combined holdings of all whales
- **Concentration Ratio**: Percentage held by largest whale
- **Activity Summary**: Distribution of activity levels
- **Behavior Analysis**: Distribution of behavior patterns
- **Recent Transfers**: Count of ERC20 token movements
- **Transaction Count**: Total transactions across whales
- **Token Activity**: Indicator of recent movement (recent/none)

## Usage Examples

### Analyze Ethereum Whales with Transfer Tracking (API Mode)
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

### Analyze Custom Whale Data with Behavior (Parameter Mode)
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
    }
  ],
  "threshold_usd": 1000000
}'
```

## Whale Concentration

The concentration_ratio metric indicates:
- **> 50%**: Extreme concentration (single whale holds majority)
- **20-50%**: High concentration
- **10-20%**: Moderate concentration
- **< 10%**: Distributed holdings

## Whale Movement Signals

The analyzer detects:
- **Whale → Exchange Flow**: Potential sell signals (distributing behavior)
- **Exchange → Whale Flow**: Potential accumulation (accumulating behavior)
- **Recent Token Transfers**: Activity indicators in top_whales entries
- **Transfer Frequency**: Shows trading velocity and engagement

## Supported Networks

- Ethereum Mainnet
- Polygon
