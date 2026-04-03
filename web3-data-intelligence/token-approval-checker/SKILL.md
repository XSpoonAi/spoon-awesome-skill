---
name: token-approval-checker
description: Check ERC20 token approvals for a wallet address, identify unlimited approvals and risky spenders, and suggest revocations.
version: 1.0.0
author: aidamidami
tags:
  - web3
  - security
  - approval
  - erc20
  - allowance
  - revoke
triggers:
  - type: keyword
    keywords:
      - token approval
      - allowance
      - revoke
      - revoke approval
      - unlimited approval
    priority: 85
parameters:
  - name: address
    type: string
    required: true
    description: Wallet address to check
  - name: chain
    type: string
    required: false
    description: Chain (ethereum, polygon, arbitrum, optimism, base)
prerequisites:
  env_vars:
    - ETHERSCAN_API_KEY
scripts:
  enabled: true
  working_directory: ./scripts
  definitions:
    - name: approval_checker
      description: Scan ERC20 approvals for an address and assess risk
      type: python
      file: approval_checker.py
      timeout: 60
---

# Token Approval Checker

Check ERC20 token approvals for a wallet address: identify **unlimited approvals** and **unknown spenders**, and get revocation suggestions.

## Features

- Scan Approval events for tokens the address has interacted with
- Flag unlimited approvals
- Distinguish known safe spenders (e.g. Uniswap routers) from unknown ones
- Output actionable revocation recommendations

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| ETHERSCAN_API_KEY | Recommended | Etherscan API Key; rate limits apply without it |

## Input Example

```json
{
  "address": "0x...",
  "chain": "ethereum"
}
```

## Best Practices

1. Review approvals periodically and revoke unused ones
2. Prioritize revoking unlimited approvals and unknown spenders
3. Use Revoke.cash or call `approve(spender, 0)` on the token contract to revoke
