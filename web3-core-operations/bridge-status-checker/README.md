# Bridge Status Checker (Track: web3-core-operations)

A comprehensive tool to track cross-chain bridge transactions and check completion status across multiple blockchain networks and bridges.

## Overview

Bridge Status Checker provides real-time monitoring of bridge transactions across major chains including Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, zkSync, and Linea. It supports multiple bridge protocols including Stargate, Wormhole, Across, and Hop.

## Features

- ✅ Multi-chain support (8+ chains)
- ✅ Multi-bridge support (Stargate, Wormhole, Across, Hop)
- ✅ Transaction status verification
- ✅ Block explorer integration
- ✅ Bridge health monitoring
- ✅ Detailed tracking information
- ✅ Next steps recommendations

## Supported Chains

- Ethereum
- Polygon
- Arbitrum
- Optimism
- Base
- Binance Smart Chain (BSC)
- zkSync Era
- Linea

## Supported Bridges

- **Stargate** - 2-5 minutes (LayerZero)
- **Wormhole** - 15-30 minutes
- **Across** - 2-10 minutes
- **Hop** - 5-15 minutes

## Installation

```bash
# No external dependencies required
python3 scripts/main.py
```

## Usage

### Check Transaction Status

```bash
echo '{
  "action": "check_tx",
  "bridge": "stargate",
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
  "source_chain": "ethereum",
  "dest_chain": "arbitrum"
}' | python3 scripts/main.py
```

### Check Bridge Health

```bash
echo '{
  "action": "health",
  "bridge": "wormhole"
}' | python3 scripts/main.py
```

## Response Format

### Check Transaction Response

```json
{
  "success": true,
  "timestamp": "2026-02-06T07:20:45.823949+00:00",
  "bridge": "stargate",
  "tx_hash": "0x1234567890abcdef...",
  "source_chain": "ethereum",
  "dest_chain": "arbitrum",
  "source_transaction": {
    "status": "success|pending|failed|error",
    "block_number": 12345678,
    "confirmed": true
  },
  "bridge_status": {
    "phase": "PENDING|IN_PROGRESS|COMPLETED",
    "estimated_completion": "2-5 minutes",
    "explorer_url": "https://..."
  },
  "tracking": {
    "check_source": "Check source tx on Etherscan",
    "check_bridge": "Track via LayerZero Scan",
    "check_destination": "Check destination on Arbiscan"
  },
  "next_steps": [
    "Wait for source transaction confirmation",
    "Monitor bridge progress",
    "Check destination chain"
  ]
}
```

### Health Check Response

```json
{
  "bridge": "wormhole",
  "status": "OPERATIONAL",
  "latency": "Normal",
  "last_incident": null,
  "note": "Check official bridge status page for real-time updates"
}
```

## Parameters

### Check Transaction (`action: "check_tx"`)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| action | string | yes | - | Must be "check_tx" |
| bridge | string | yes | - | Bridge protocol (stargate, wormhole, across, hop) |
| tx_hash | string | yes | - | Transaction hash to check |
| source_chain | string | yes | ethereum | Source blockchain |
| dest_chain | string | no | null | Destination blockchain |

### Health Check (`action: "health"`)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| action | string | yes | - | Must be "health" |
| bridge | string | yes | - | Bridge protocol to check |

## Error Handling

The script handles various error scenarios:

- **Invalid bridge**: Returns error for unsupported bridges
- **Network errors**: Gracefully handles API timeouts
- **Missing parameters**: Validates required fields
- **Chain mismatch**: Checks if transaction hash exists on specified chain

## Use Cases

1. **Monitor bridge progress** - Track real-time status of cross-chain transactions
2. **Troubleshoot stuck transactions** - Identify where transactions are failing
3. **Monitor bridge health** - Check if bridges are operational
4. **Automate operations** - Integrate into workflows for automated monitoring
5. **User support** - Help users understand their bridge transaction status

## API Integration

The tool reads JSON from stdin and outputs JSON, making it easy to integrate with other tools:

```bash
# Pipe from another application
some_command | python3 scripts/main.py

# Store output for processing
echo '{"action": "check_tx", ...}' | python3 scripts/main.py > result.json
```

## Chain Explorers Used

- **Etherscan** (Ethereum)
- **Polygonscan** (Polygon)
- **Arbiscan** (Arbitrum)
- **Optimistic Etherscan** (Optimism)
- **Basescan** (Base)
- **BscScan** (BSC)
- **zkSync Explorer** (zkSync)
- **Lineascan** (Linea)

## Configuration

API keys can be set as environment variables for enhanced rate limits:

```bash
export ETHERSCAN_API_KEY="your_api_key"
export POLYGONSCAN_API_KEY="your_api_key"
export ARBISCAN_API_KEY="your_api_key"
# ... etc for other chains
```

## Dependencies

- Python 3.7+
- No external packages required (uses standard library)

## License

Part of the SpoonOS Skills Micro Challenge submission
