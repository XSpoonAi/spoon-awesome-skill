# Bridge Status Checker

Real-time cross-chain bridge transaction tracking using direct RPC queries. Monitor bridge transactions across 8+ EVM chains (Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, zkSync, Linea) and 4 bridge protocols (Stargate, Wormhole, Across, Hop).

## Features

✅ **Real RPC Queries** - Direct blockchain data (no block explorer API keys needed)
✅ **Multi-Chain Support** - Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, zkSync, Linea
✅ **Bridge Protocols** - Stargate, Wormhole, Across, Hop
✅ **Confirmation Tracking** - Real block confirmations from live blockchain
✅ **Health Monitoring** - Bridge contract availability checks
✅ **Error Handling** - Comprehensive validation and error messages

## Installation

```bash
# Install dependencies
pip3 install web3

# Test installation
echo '{"action": "chains"}' | python3 scripts/main.py
```

## Quick Start

### Check Transaction Status

Get real transaction status from blockchain RPC:

```bash
echo '{
  "action": "check_tx",
  "bridge": "stargate",
  "tx_hash": "0x32bf66242692f3b7cc364ada2a87354bacaf86f99bfeaefd8a78400314fcfc48",
  "source_chain": "ethereum"
}' | python3 scripts/main.py
```

**Real Output (Block #24398945, Ethereum):**

```json
{
  "success": true,
  "timestamp": "2026-02-06T16:22:06.986966+00:00",
  "bridge": {
    "name": "Stargate (LayerZero)",
    "protocol": "stargate"
  },
  "source_transaction": {
    "hash": "0x32bf66242692f3b7cc364ada2a87354bacaf86f99bfeaefd8a78400314fcfc48",
    "chain": "Ethereum",
    "status": "success",
    "block_number": 24398945,
    "confirmations": 2,
    "gas_used": 21000,
    "from": "0xae2885E0E7A6c5f99b93B4dBC43D206C7cf67c7E",
    "to": "0xae2885E0E7A6c5f99b93B4dBC43D206C7cf67c7E",
    "explorer_url": "https://etherscan.io/tx/0x32bf66..."
  },
  "bridge_status": {
    "phase": "CONFIRMING - 2 confirmations (waiting for 10 more)",
    "estimated_completion": "2-5 minutes",
    "bridge_contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
  },
  "next_steps": [
    "🔗 Transaction confirming: 2/12 blocks",
    "⏳ Wait for sufficient confirmations before bridge processes"
  ],
  "rpc_used": "https://eth-mainnet.public.blastapi.io"
}
```

### Check Bridge Health

```bash
echo '{"action": "health", "bridge": "stargate"}' | python3 scripts/main.py
```

### List Supported Chains

```bash
echo '{"action": "chains"}' | python3 scripts/main.py
```

### List Supported Bridges

```bash
echo '{"action": "bridges"}' | python3 scripts/main.py
```

## Supported Chains

| Chain | Chain ID | RPC Provider |
|-------|----------|--------------|
| Ethereum | 1 | Blast API |
| Polygon | 137 | Polygon RPC |
| Arbitrum | 42161 | Arbitrum RPC |
| Optimism | 10 | Optimism RPC |
| Base | 8453 | Base RPC |
| BSC | 56 | BSC Dataseed |
| zkSync | 324 | zkSync Era RPC |
| Linea | 59144 | Linea RPC |

## Supported Bridges

- **Stargate** (LayerZero): 2-5 minutes
- **Wormhole**: 15-30 minutes
- **Across**: 2-10 minutes
- **Hop**: 5-15 minutes

## API Actions

### `check_tx` - Check Transaction Status

Queries blockchain RPC for transaction receipt and status.

**Parameters:**
- `action` (string): "check_tx"
- `bridge` (string): "stargate", "wormhole", "across", "hop"
- `tx_hash` (string): Transaction hash (0x...)
- `source_chain` (string): "ethereum", "polygon", "arbitrum", etc.
- `dest_chain` (optional): Destination chain

### `health` - Check Bridge Health

Verifies bridge contract availability across chains.

**Parameters:**
- `action` (string): "health"
- `bridge` (string): Bridge protocol name

### `chains` - List Supported Chains

Lists all available blockchain networks with RPC endpoints.

### `bridges` - List Supported Bridges

Lists all supported bridge protocols.

## Error Handling

Errors include descriptive messages:

```json
{
  "success": false,
  "error": "validation_error",
  "message": "Invalid transaction hash format (expected 66 char hex with 0x prefix)"
}
```

## How It Works

### Direct RPC Architecture

Uses JSON-RPC calls to query blockchain directly:

```
eth_getTransactionReceipt → Get transaction status
eth_getTransaction → Get transaction details
eth_blockNumber → Get current block
eth_getCode → Verify contract deployment
```

**No API Keys Required** - Queries public RPC endpoints.

## Dependencies

- `web3.py` >= 6.0
- Python 3.8+
