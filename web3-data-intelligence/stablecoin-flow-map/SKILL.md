---
name: stablecoin-flow-map
track: web3-data-intelligence
version: 0.2.0
summary: Real stablecoin flow mapping with blockchain API data
---

## Description

Map stablecoin flows between protocols, exchanges, and wallets using real blockchain data. Tracks liquidity movement patterns across Ethereum, Polygon, and other networks. Identifies where USDC, USDT, and DAI are flowing.

## Inputs (API Mode)

```json
{
  "use_api": true,
  "network": "ethereum",
  "stablecoin": "USDC",
  "min_amount_usd": 100000
}
```

## Inputs (Parameter Mode)

```json
{
  "network": "ethereum",
  "stablecoin": "USDC",
  "min_amount_usd": 100000,
  "flows": [
    {
      "from": "0x1234...",
      "to": "0x5678...",
      "amount_usd": 250000,
      "stablecoin": "USDC",
      "timestamp": "2026-02-07T08:00:00Z"
    }
  ]
}
```

## Outputs

```json
{
  "ok": true,
  "data": {
    "source": "blockchain_api",
    "network": "ethereum",
    "stablecoin": "USDC",
    "total_flows": 42,
    "total_volume_usd": 5250000.0,
    "unique_source_addresses": 28,
    "unique_dest_addresses": 15,
    "flow_map": [
      {
        "from": "protocol:uniswap",
        "to": "exchange:binance",
        "count": 8,
        "volume_usd": 850000.0,
        "avg_size_usd": 106250.0
      }
    ],
    "top_sources": [
      ["protocol:uniswap", 12],
      ["wallet", 8]
    ],
    "top_destinations": [
      ["exchange:binance", 15],
      ["protocol:aave", 9]
    ],
    "analysis_timestamp": "2026-02-07T08:30:00Z"
  }
}
```

## Usage

### Fetch Real Ethereum Flows
```bash
python scripts/main.py --params '{"use_api":true,"network":"ethereum","stablecoin":"USDC","min_amount_usd":100000}'
```

### Map Polygon USDT Flows
```bash
python scripts/main.py --params '{"use_api":true,"network":"polygon","stablecoin":"USDT","min_amount_usd":50000}'
```

### Analyze Custom Flows
```bash
python scripts/main.py --params '{"network":"ethereum","stablecoin":"USDC","flows":[{"from":"0x...","to":"0x...","amount_usd":250000}]}'
```

## Examples

### Example 1: Ethereum USDC Flows (API)
```bash
$ python scripts/main.py --params '{"use_api":true,"network":"ethereum","stablecoin":"USDC"}'
{
  "ok": true,
  "data": {
    "source": "blockchain_api",
    "total_flows": 42,
    "total_volume_usd": 5250000.0,
    "flow_map": [
      {
        "from": "protocol:uniswap",
        "to": "exchange:binance",
        "count": 8,
        "volume_usd": 850000.0
      }
    ]
  }
}
```

### Example 2: Custom Flow Analysis
```bash
$ python scripts/main.py --params '{"network":"ethereum","stablecoin":"USDC","flows":[{"from":"0x1111...","to":"0x2222...","amount_usd":500000}]}'
{
  "ok": true,
  "data": {
    "source": "parameters",
    "total_flows": 1,
    "total_volume_usd": 500000.0
  }
}
```

## Supported Networks

- **ethereum** - USDC, USDT, DAI, BUSD
- **polygon** - USDC, USDT, DAI
- **arbitrum** - (expandable)
- **optimism** - (expandable)

## Address Classifications

- **protocol:XXX** - Major DeFi protocols (Uniswap, Aave, Curve, Lido, Compound)
- **exchange:XXX** - Centralized exchange deposits (Binance, Coinbase, Kraken)
- **wallet** - Regular user wallets/addresses
