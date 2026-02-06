---
name: contract-event-tail
track: web3-core-operations
version: 0.1.0
summary: Monitor and retrieve smart contract events from multiple chains
---

## Description

Monitor and retrieve blockchain event logs from smart contracts in real-time across multiple EVM chains including Ethereum, Polygon, Arbitrum, and Optimism.

## Inputs

```json
{
  "contract_address": "Smart contract address (0x...)",
  "from_block": "Starting block number",
  "to_block": "Ending block number",
  "chain": "Blockchain network (ethereum, polygon, arbitrum, optimism)"
}
```

## Outputs

```json
{
  "ok": true,
  "data": {
    "success": true,
    "timestamp": "2026-02-06T07:29:44.015910+00:00",
    "contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "chain": "ethereum",
    "events": [],
    "total_events": 0
  }
}
```

## Usage

### Demo Mode
```bash
python scripts/main.py --demo
```

### With Parameters
```bash
echo '{"contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "from_block": 17000000, "to_block": 17000100, "chain": "ethereum"}' | python3 scripts/main.py
```

## Examples

### Example 1: Monitor USDC Events
```bash
$ echo '{"contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "from_block": 17000000, "to_block": 17000100}' | python3 scripts/main.py
{
  "success": true,
  "timestamp": "2026-02-06T07:29:44.015910+00:00",
  "contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  "chain": "ethereum",
  "events": [],
  "total_events": 0
}
```

### Example 2: Polygon Network
```bash
$ echo '{"contract_address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "chain": "polygon"}' | python3 scripts/main.py
{
  "success": true,
  "timestamp": "2026-02-06T07:29:44.015910+00:00",
  "contract": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
  "chain": "polygon",
  "events": [],
  "total_events": 0
}
```

## Error Handling

When an error occurs, the skill returns:

```json
{
  "ok": false,
  "error": "Error description",
  "details": {
    "contract": "invalid format"
  }
}
```
