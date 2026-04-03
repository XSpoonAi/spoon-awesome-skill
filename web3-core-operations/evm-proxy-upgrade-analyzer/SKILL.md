---
name: evm-proxy-upgrade-analyzer
track: web3-core-operations
version: 0.1.0
summary: Detect EVM proxy patterns (EIP-1967, Beacon, EIP-1167 minimal proxy) and report implementation/admin/beacon addresses plus upgrade risk flags.
description: Detect common EVM proxy patterns and extract upgrade-related addresses and risk signals.
author: guangyusong
tags:
  - evm
  - proxy
  - eip-1967
  - uups
  - security
---

## Description

Detect common EVM proxy patterns and report implementation/admin/beacon addresses along with basic upgrade risk flags.

## Inputs

```json
{
  "rpc_url": "https://...",
  "proxy_address": "0x...",
  "block": "latest",
  "timeout_seconds": 20,
  "check_uups": true,
  "check_beacon_impl": true
}
```

## Outputs

Success:
```json
{
  "ok": true,
  "data": {
    "demo": false,
    "proxy_address": "0x...",
    "proxy_type": "NOT_A_CONTRACT|EIP-1167_MINIMAL|EIP-1967_PROXY|EIP-1967_BEACON|UNKNOWN",
    "implementation_address": "0x..." ,
    "admin_address": "0x...",
    "beacon_address": "0x...",
    "beacon_implementation_address": "0x...",
    "is_uups": true,
    "risk_score": 0,
    "risk_flags": []
  }
}
```

Error:
```json
{
  "ok": false,
  "error": "...",
  "details": {"message": "..."}
}
```

## Usage

Demo mode (offline):
```bash
python3 scripts/main.py --demo
```

With parameters:
```bash
python3 scripts/main.py --params '{"rpc_url":"https://...","proxy_address":"0x..."}'
```

Via stdin:
```bash
echo '{"rpc_url":"https://...","proxy_address":"0x..."}' | python3 scripts/main.py
```

## Error Handling

All errors return JSON with `ok:false` and exit with a non-zero code.
