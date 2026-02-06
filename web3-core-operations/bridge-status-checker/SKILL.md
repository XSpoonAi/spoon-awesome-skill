---
name: bridge-status-checker
track: web3-core-operations
version: 0.1.0
summary: Track cross-chain bridge transactions and check completion status
---

## Description

Track cross-chain bridge transactions and check completion status across multiple chains and bridge protocols. Supports Stargate, Wormhole, Across, and Hop bridges.

## Inputs

```json
{
  "action": "check_tx|health",
  "bridge": "stargate|wormhole|across|hop",
  "tx_hash": "Transaction hash",
  "source_chain": "ethereum|polygon|arbitrum|optimism",
  "dest_chain": "Destination chain"
}
```

## Outputs

```json
{
  "ok": true,
  "data": {
    "success": true,
    "bridge": "stargate",
    "tx_hash": "0x...",
    "source_chain": "ethereum",
    "status": "completed"
  }
}
```

## Usage

### Check Transaction Status
```bash
echo '{"action": "check_tx", "bridge": "stargate", "tx_hash": "0x...", "source_chain": "ethereum"}' | python3 scripts/main.py
```

### Check Bridge Health
```bash
echo '{"action": "health", "bridge": "wormhole"}' | python3 scripts/main.py
```

### Demo Mode
```bash
python scripts/main.py --demo
```

## Examples

### Example 1: Check Stargate Transaction
```bash
$ echo '{"action": "check_tx", "bridge": "stargate", "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "source_chain": "ethereum", "dest_chain": "arbitrum"}' | python3 scripts/main.py
{
  "success": true,
  "timestamp": "2026-02-06T07:31:06.856041+00:00",
  "bridge": "stargate",
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
  "source_chain": "ethereum",
  "dest_chain": "arbitrum",
  "status": "completed"
}
```

## Error Handling

When an error occurs, the skill returns:

```json
{
  "ok": false,
  "error": "Error description",
  "details": {
    "bridge": "Unsupported bridge"
  }
}
```
