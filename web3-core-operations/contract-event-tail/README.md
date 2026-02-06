# Contract Event Tail

Real-time contract event monitoring using direct RPC eth_getLogs. Retrieve all ERC20 Transfer events, Swap events, or custom events from any smart contract across 6 EVM chains without requiring API keys.

## Features

✅ **Real RPC Queries** - eth_getLogs directly from blockchain nodes
✅ **Multi-Chain** - Ethereum, Polygon, Arbitrum, Optimism, Base, BSC
✅ **Topic Filtering** - Filter by event signature and indexed parameters  
✅ **No API Keys** - Works with public RPC endpoints
✅ **Common Event Registry** - Pre-configured Transfer, Approval, Swap events
✅ **Hex-Encoded Output** - Full event logs with topics and data

## Installation

```bash
pip3 install web3
echo '{"action": "chains"}' | python3 scripts/main.py
```

## Get Contract Events

Retrieve 641 real USDC Transfer events (blocks 24398975-24398980):

```bash
echo '{
  "action": "get_logs",
  "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  "from_block": 24398975,
  "to_block": 24398980,
  "chain": "ethereum",
  "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
}' | python3 scripts/main.py
```

## Get Contract Info

```bash
echo '{
  "action": "info",
  "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  "chain": "ethereum"
}' | python3 scripts/main.py
```

## List Common Events

```bash
echo '{"action": "events"}' | python3 scripts/main.py
```

## Supported Chains

Ethereum, Polygon, Arbitrum, Optimism, Base, BSC

## Common Events

- **Transfer**: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
- **Approval**: 0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925
- **Swap**: 0xd78ad95fa46012529f48e5a17c6a6ee5edcf5cc4de798e919b15e8a1e2e1688f
