---
name: contract-event-tail
track: web3-core-operations
version: 0.1.0
summary: Monitor and tail smart contract events in real-time
---

## Description

Subscribe to contract events and stream them in real-time.

## Inputs

```json
{
  "contract": "0x...",
  "events": ["Transfer", "Approval"],
  "from_block": "latest"
}
```

## Usage

```bash
python scripts/main.py --demo
```
