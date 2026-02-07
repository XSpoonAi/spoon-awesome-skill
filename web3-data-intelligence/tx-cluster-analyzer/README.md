# tx-cluster-analyzer

Analyze and cluster related blockchain transactions using real RPC data.

## Overview

This skill analyzes and clusters blockchain transactions using real RPC endpoints. It fetches transaction details, builds address relationship graphs, detects transaction patterns (fan-out, fan-in, chains), and provides comprehensive flow analysis for transaction clustering.

## Features

- ✅ Real blockchain RPC integration (eth_getTransactionByHash)
- ✅ Multi-network support (Ethereum, Polygon)
- ✅ Transaction relationship graph building
- ✅ Pattern detection (fan-out, fan-in, chain, complex)
- ✅ Address flow analysis (in/out degree tracking)
- ✅ Value and nonce aggregation
- ✅ High-value address identification
- ✅ Graph edge ranking
- ✅ Dual-mode operation (API + Parameter)

## Usage

### API Mode (Real Blockchain Data)
```bash
python scripts/main.py --params '{"use_api": true, "network": "ethereum", "tx_hashes": ["0x...", "0x..."]}'
```

### Parameter Mode (Custom Transaction Data)
```bash
python scripts/main.py --params '{"use_api": false, "network": "ethereum", "transactions": [{"hash": "0x...", "from": "0x...", "to": "0x...", "value": "0x..."}]}'
```

## Parameters

### API Mode Parameters
- `use_api` (boolean, required): Enable RPC integration
- `network` (string, required): "ethereum" or "polygon"
- `tx_hashes` (array, required): Transaction hashes to fetch (max 50 per request)

### Parameter Mode Parameters
- `use_api` (boolean, required): Disable API (false)
- `network` (string, required): Network identifier
- `transactions` (array, required): Array of transaction objects with:
  - `hash`: Transaction hash
  - `from`: Sender address
  - `to`: Recipient address (or null for contract creation)
  - `value`: Value transferred (hex or integer)
  - `nonce`: Transaction nonce

## Output

Returns JSON with:
- `status`: "success" or "error"
- `source`: "blockchain_api" or "parameters"
- `network`: Analyzed network
- `cluster_size`: Number of transactions analyzed
- `unique_addresses`: Total unique addresses in cluster
- `total_value_eth`: Total ETH transferred
- `avg_tx_value_eth`: Average transaction value
- `pattern_type`: Detected pattern (single, fan-out, fan-in, chain, complex)
- `pattern_stats`: Source/sink/intermediate address counts
- `address_graph`: Node and edge representation
- `highest_value_addresses`: Top addresses by flow volume

## Pattern Detection

- **single_transaction**: Only one transaction
- **fan_out**: One source sending to multiple destinations (fund splitting, airdrops)
- **fan_in**: Multiple sources sending to one destination (fund consolidation, bridges)
- **chain**: Linear sequence of connected transactions (A→B→C→...)
- **complex**: Mixed patterns with multiple sources and sinks

## Transaction Graph

The response includes a graph representing address relationships:

**Nodes:**
- Address information
- Node type (wallet, contract)
- In-degree (incoming transactions)
- Out-degree (outgoing transactions)
- Net flow (positive = net receiver, negative = net sender)

**Edges:**
- Source and destination addresses
- Number of transactions between addresses

## Examples

### Analyze Multiple Transactions on Ethereum (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "ethereum",
  "tx_hashes": [
    "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "0x2345678901bcdef0123456789abcdef0123456789abcdef0123456789abcdef0",
    "0x3456789012cdef01234567890abcdef01234567890abcdef01234567890abcdef1"
  ]
}'
```

### Analyze Polygon Transactions (API Mode)
```bash
python scripts/main.py --params '{
  "use_api": true,
  "network": "polygon",
  "tx_hashes": [
    "0x...",
    "0x..."
  ]
}'
```

### Analyze Custom Transaction Cluster (Parameter Mode)
```bash
python scripts/main.py --params '{
  "use_api": false,
  "network": "ethereum",
  "transactions": [
    {
      "hash": "0x1234...",
      "from": "0x1111111111111111111111111111111111111111",
      "to": "0x2222222222222222222222222222222222222222",
      "value": "0x0de0b6b3a7640000",
      "nonce": 0
    },
    {
      "hash": "0x5678...",
      "from": "0x1111111111111111111111111111111111111111",
      "to": "0x3333333333333333333333333333333333333333",
      "value": "0x0de0b6b3a7640000",
      "nonce": 1
    }
  ]
}'
```

## Graph Metrics

**Degree Centrality:**
- High in-degree: Addresses that receive from many sources (aggregators, contracts)
- High out-degree: Addresses that send to many destinations (distributors)

**Flow Analysis:**
- Positive net_flow: Net receiver of funds
- Negative net_flow: Net sender of funds

## Supported Networks

- Ethereum Mainnet
- Polygon

## Category

web3-data-intelligence
