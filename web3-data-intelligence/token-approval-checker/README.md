# Token Approval Checker

Scan ERC20 token approvals for a wallet address: identify **unlimited approvals** and **unknown spenders**, and get revocation suggestions.

## Features

- Fetch ERC20 transfer history via Etherscan-style API to get tokens the address has interacted with
- Query `Approval` events per token and parse spender and allowance
- Flag **unlimited approval** (`type(uint256).max`)
- Distinguish **known safe spenders** (e.g. Uniswap, 1inch routers) from **unknown spenders**
- Output risk level and revocation recommendations

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| ETHERSCAN_API_KEY | Recommended | Etherscan API Key; rate limits apply without it |

For other chains: `POLYGONSCAN_API_KEY`, `ARBISCAN_API_KEY`, `OPTIMISM_API_KEY`, `BASESCAN_API_KEY`.

## Input / Output

**Input (JSON via stdin):**

```json
{
  "address": "0x...",
  "chain": "ethereum"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | Wallet address to check |
| chain | string | No | ethereum / polygon / arbitrum / optimism / base; default ethereum |

**Output:** JSON with `approvals` list, `summary`, and `recommendations`.

Each approval entry:

- `token_address`: Token contract address
- `spender`: Approved spender address
- `value`: Allowance (wei)
- `unlimited`: Whether the approval is unlimited
- `risk`: low / medium / high
- `spender_known`: Whether the spender is in the known-safe list

## Risk Levels

- **high**: Unlimited approval and unknown spender; revoke first
- **medium**: Unlimited but known spender, or limited amount but unknown spender
- **low**: Known spender with limited amount

## Known Safe Spenders (examples)

- Uniswap V2/V3 Router
- 1inch, 0x aggregators
- Common DEX routers per chain (see `KNOWN_SAFE_SPENDERS` in script)

## CLI Example

```bash
# Check an Ethereum address
echo '{"address":"0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae","chain":"ethereum"}' | python3 scripts/approval_checker.py
```

## How to Revoke

- Use [Revoke.cash](https://revoke.cash) or similar tools
- Or call the token contract: `approve(spender, 0)`

## Security Note

- This tool only reads on-chain data and suggests risks; it does not send transactions
- Unknown spenders are not necessarily malicious; they are simply not in the built-in whitelist—use your own judgment
