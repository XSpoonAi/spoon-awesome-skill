# stablecoin-flow-map

Map and track stablecoin flows across DeFi protocols and exchanges using real blockchain data.

## Overview

This skill analyzes stablecoin transfer flows between major DeFi protocols, smart contracts, and centralized exchanges. It classifies transaction senders and receivers to understand capital movement patterns.

## Features

- ✅ Real blockchain API integration (JSON-RPC txpool_content)
- ✅ Multi-stablecoin support (USDC, USDT, DAI, BUSD)
- ✅ Address classification (Protocol, Exchange, Wallet)
- ✅ Network support (Ethereum, Polygon)
- ✅ Minimum amount filtering (USD-based)
- ✅ Volume aggregation and network mapping
- ✅ Top sources/destinations ranking
- ✅ Stablecoin breakdown analytics
- ✅ Dual-mode operation (API + Parameter)

## Usage

### API Mode (Live Blockchain Data)
```bash
python scripts/main.py --params '{"use_api": true, "network": "ethereum", "stablecoin": "USDC", "min_amount_usd": 100000}'
```

### Parameter Mode (Custom Flow Analysis)
```bash
python scripts/main.py --params '{"use_api": false, "flows": [{"from": "0x...", "to": "0x...", "amount": "1000000", "stablecoin": "USDC"}]}'
```

## Parameters

### API Mode Parameters
- `use_api` (boolean, required): Enable live blockchain data fetching
- `network` (string, required): Blockchain network - "ethereum" or "polygon"
- `stablecoin` (string, required): Stablecoin to track - "USDC", "USDT", "DAI", or "BUSD"
- `min_amount_usd` (number, required): Minimum transfer amount in USD

### Parameter Mode Parameters
- `use_api` (boolean, required): Disable live API (false)
- `flows` (array, required): Custom flow objects with from/to addresses, amount, and stablecoin

## Output

Returns JSON with:
- `status`: "success" or "error"
- `network`: Analyzed blockchain network
- `stablecoin`: Tracked stablecoin symbol
- `source`: "api" (live blockchain) or "parameters" (custom data)
- `flow_count`: Number of flows analyzed
- `total_volume_usd`: Total USD volume in flow network
- `stablecoin_breakdown`: Volume by stablecoin
- `flow_map`: Network graph structure with nodes and edges
- `top_sources`: Highest volume sending addresses/protocols
- `top_destinations`: Highest volume receiving addresses/protocols
- `address_types`: Breakdown by classification (protocol, exchange, wallet)

## Examples

### Monitor USDC on Ethereum (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "ethereum",
  "stablecoin": "USDC",
  "min_amount_usd": 500000
}'
```

### Analyze USDT on Polygon (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "polygon",
  "stablecoin": "USDT",
  "min_amount_usd": 100000
}'
```

### Custom Flow Analysis (Parameter Mode)
```bash
python scripts/main.py --params '{
  "use_api": false,
  "flows": [
    {
      "from": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "to": "0x3c3a81e81dc49A522A592995a2fa8a90B6b8cfFb",
      "amount": "1000000000000",
      "stablecoin": "USDC"
    }
  ]
}'
```

## Address Classification

Addresses are automatically classified into three categories:

- **Protocol** (e.g., "protocol:Uniswap"): DeFi protocols and smart contracts
- **Exchange** (e.g., "exchange:Binance"): Centralized exchange addresses
- **Wallet**: Unknown or individual wallet addresses

### Tracked Protocols
- **DEX**: Uniswap (v2/v3), SushiSwap
- **Lending**: Aave, Compound, Curve
- **Staking**: Lido
- **Other**: Balancer, Maker

### Tracked Exchanges
- Binance
- Coinbase
- Kraken

## Supported Networks

- **Ethereum Mainnet**: Full USDC, USDT, DAI, BUSD support
- **Polygon**: Full USDC, USDT, DAI, BUSD support

## Category

web3-data-intelligence
