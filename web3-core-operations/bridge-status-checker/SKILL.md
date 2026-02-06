---
name: bridge-status-checker
track: web3-core-operations
version: 0.1.0
summary: Check cross-chain bridge transaction status
---

## Description

Track bridge transactions across chains and check completion status.

## Inputs

```json
{
  "bridge": "arbitrum|optimism|polygon",
  "tx_hash": "0x...",
  "source_chain": "ethereum"
}
```

## Usage

```bash
python scripts/main.py --demo
```
