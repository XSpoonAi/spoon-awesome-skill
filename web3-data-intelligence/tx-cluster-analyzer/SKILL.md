---
name: tx-cluster-analyzer
track: web3-data-intelligence
version: 0.2.0
summary: Analyze and cluster related blockchain transactions using real RPC data
---

## Description

Analyzes and clusters blockchain transactions using real RPC data. Detects transaction patterns (fan-out, fan-in, chains), builds address relationship graphs, and identifies transaction flows between addresses.

## Features

- Real blockchain RPC integration (eth_getTransactionByHash)
- Multi-network support (Ethereum, Polygon)
- Transaction relationship graph building
- Pattern detection (single, fan-out, fan-in, chain, complex)
- Address flow analysis (inbound/outbound)
- Value aggregation and metric calculation
- Dual-mode operation (API + Parameter)

## Inputs

### API Mode
```json
{
  "use_api": true,
  "network": "ethereum",
  "tx_hashes": ["0xhash1", "0xhash2", "0xhash3"]
}
```

### Parameter Mode
```json
{
  "use_api": false,
  "network": "ethereum",
  "transactions": [
    {
      "hash": "0x...",
      "from": "0x...",
      "to": "0x...",
      "value": "0x...",
      "nonce": 0
    }
  ]
}
```

## Outputs

```json
{
  "ok": true,
  "data": {
    "status": "success",
    "source": "blockchain_api",
    "network": "ethereum",
    "cluster_size": 5,
    "transactions_analyzed": 5,
    "unique_addresses": 8,
    "total_value_eth": 2.5,
    "avg_tx_value_eth": 0.5,
    "pattern_type": "fan_out",
    "pattern_stats": {
      "source_addresses": 1,
      "sink_addresses": 3,
      "intermediate_addresses": 4
    },
    "address_graph": {
      "nodes": [
        {
          "address": "0x...",
          "type": "wallet",
          "in_degree": 0,
          "out_degree": 3,
          "net_flow_eth": -2.5
        }
      ],
      "edges": [
        {
          "from": "0x...",
          "to": "0x...",
          "count": 1
        }
      ]
    },
    "highest_value_addresses": [...],
    "analysis_timestamp": "2026-02-07T09:30:00.000Z"
  }
}
```

## Parameters

### API Mode Parameters
- `use_api` (boolean, required): Enable blockchain RPC integration
- `network` (string, required): "ethereum" or "polygon"
- `tx_hashes` (array, required): Array of transaction hashes to fetch and analyze

### Parameter Mode Parameters
- `use_api` (boolean, required): Disable API (false)
- `network` (string, required): Network identifier
- `transactions` (array, required): Transaction objects with hash, from, to, value

## Pattern Types

- **single_transaction**: Only one transaction in cluster
- **fan_out**: One source address sending to multiple destinations (fund splitting)
- **fan_in**: Multiple source addresses sending to one destination (fund consolidation)
- **chain**: Linear sequence of transactions (A→B→C→...)
- **complex**: Mixed pattern with multiple sources and sinks

## Usage Examples

### Analyze Transaction Cluster on Ethereum (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "ethereum",
  "tx_hashes": [
    "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd"
  ]
}'
```

### Analyze Custom Transactions (Parameter Mode)
```bash
python scripts/main.py --params '{
  "use_api": false,
  "network": "ethereum",
  "transactions": [
    {
      "hash": "0x...",
      "from": "0x1111111111111111111111111111111111111111",
      "to": "0x2222222222222222222222222222222222222222",
      "value": "0x0de0b6b3a7640000",
      "nonce": 0
    },
    {
      "hash": "0x...",
      "from": "0x1111111111111111111111111111111111111111",
      "to": "0x3333333333333333333333333333333333333333",
      "value": "0x0de0b6b3a7640000",
      "nonce": 1
    }
  ]
}'
```

## Address Graph Structure

The response includes a graph representation:
- **nodes**: Address entities with degree metrics and net flow
  - `in_degree`: Number of incoming transactions
  - `out_degree`: Number of outgoing transactions
  - `net_flow_eth`: Net ETH flow (positive = receiver, negative = sender)
- **edges**: Relationships between addresses
  - `from`: Source address
  - `to`: Destination address
  - `count`: Number of transactions on this edge

## Supported Networks

- Ethereum Mainnet
- Polygon
