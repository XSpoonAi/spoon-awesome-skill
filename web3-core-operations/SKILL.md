# ERC20 Allowance Manager - Skill Specification

## Skill ID
`erc20-allowance-manager`

## Category
Web3 Core Operations

## Overview
Comprehensive ERC20 token allowance management system with real blockchain queries via RPC, supporting multiple approval strategies, security risk assessment, and batch operations.

## Capabilities

### Core Functions
1. **check** - Query current allowance for token/spender pair
2. **approve** - Set token allowance with multiple strategies
3. **revoke** - Revoke token allowance (set to 0)
4. **batch_check** - Check allowances for multiple spenders simultaneously

### Approval Strategies
- `unlimited` - Approve maximum uint256 (infinite)
- `exact` - Approve specific amount
- `increase` - Increase existing allowance
- `safe` - Safe approval pattern (revoke then approve)

## Input Format

### Parameters
```json
{
  "owner": "0x...",           // Token owner wallet address (required)
  "token": "0x...",           // ERC20 token contract address (required)
  "action": "check|approve|revoke|batch_check",  // Operation (default: check)
  "spender": "0x...",         // Spender contract address (required for check/approve/revoke)
  "amount": "1000.00",        // Amount to approve (optional, for exact/increase)
  "strategy": "exact",        // Approval strategy (default: exact)
  "spenders": ["0x...", "0x..."]  // Array of spenders (required for batch_check)
}
```

## Output Format

### Success Response (check action)
```json
{
  "success": true,
  "action": "check",
  "owner": "0x...",
  "token": {
    "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "symbol": "USDC",
    "decimals": 6,
    "name": "USD Coin"
  },
  "spender": {
    "address": "0x68b3465833fb72B5A828cCEEB955439B22B36987",
    "name": "Uniswap V3 Router",
    "category": "dex",
    "risk_level": "low"
  },
  "allowance": {
    "amount": "1000000000",     // Raw wei/units
    "amount_decimal": 1000000.0, // Decimal-adjusted
    "is_unlimited": false,
    "expires_at": null
  },
  "risk_assessment": {
    "is_unlimited": false,
    "is_suspicious_spender": false,
    "balance_ratio": 0.5,
    "risk_level": "low",
    "recommendations": []
  },
  "block_number": 24398547,
  "rpc_used": "https://eth-mainnet.public.blastapi.io",
  "timestamp": "2026-02-06T20:36:00Z"
}
```

### Success Response (approve action)
```json
{
  "success": true,
  "action": "approve",
  "owner": "0x...",
  "token": {...},
  "spender": {...},
  "approval": {
    "amount": "1000000000",
    "amount_decimal": 1000.0,
    "strategy": "exact",
    "transaction": {
      "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "data": "0x095ea7b3...",
      "gas_limit": 60000,
      "gas_price_gwei": 35.0,
      "estimated_cost_usd": 2.50
    }
  },
  "block_number": 24398547,
  "timestamp": "2026-02-06T20:36:00Z"
}
```

### Success Response (batch_check action)
```json
{
  "success": true,
  "action": "batch_check",
  "owner": "0x...",
  "token": {...},
  "results": [
    {
      "spender": {...},
      "allowance": {...},
      "risk_assessment": {...}
    }
  ],
  "summary": {
    "total_checked": 3,
    "unlimited_approvals": 1,
    "suspicious_spenders": 0
  },
  "timestamp": "2026-02-06T20:36:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "validation_error|connection_error|dependency_error|system_error",
  "message": "Human-readable error description"
}
```

## Error Handling

| Error Type | Cause | Solution |
|-----------|-------|----------|
| `dependency_error` | web3.py not installed | Run `pip install web3` |
| `connection_error` | RPC endpoint unreachable | Check ETHEREUM_RPC environment variable or RPC endpoint availability |
| `validation_error` | Invalid address/token format | Verify Ethereum address format (0x...{40 hex chars}) |
| `system_error` | Unexpected error | Check logs and retry |

## Configuration

### Environment Variables
```bash
ETHEREUM_RPC=https://eth-mainnet.public.blastapi.io  # Custom RPC endpoint (optional)
```

### Known Spenders Registry
- Uniswap V3 Router: `0xE592427A0AEce92De3Edee1F18E0157C05861564`
- Uniswap V2 Router: `0x7a250d5630b4cf539739df2c5dacb4c659f2488d`
- 1inch Router: `0x1111111254fb6c44bac0bed2854e76f90643097d`
- OpenSea Permit2: `0x000000000022D473030F116dFC393057B8271AC6`
- Permit2: `0x000000000022D473030F116dFC393057B8271AC6`

### Token Registry
- USDC: `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48` (6 decimals)
- USDT: `0xdac17f958d2ee523a2206206994597c13d831ec7` (6 decimals)
- WETH: `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` (18 decimals)
- DAI: `0x6b175474e89094c44da98b954eedeac495271d0f` (18 decimals)
- WBTC: `0x2260fac5e5542a773aa44fbcff9d822a3ecee8e7` (8 decimals)

## Dependencies

### Required
- `web3` >= 6.0 (Install via: `pip install web3`)
- Python 3.8+

### Optional
- None

## Blockchain Integration

### RPC Method
- **Provider**: Ethereum mainnet via RPC endpoint
- **Methods Used**:
  - `eth_blockNumber` - Get current block
  - `eth_call` - Query allowance(owner, spender)
  - `eth_getBalance` - Get token balance

### Smart Contracts
- **ERC20 Interface**: Standard allowance() function
- **Permit2**: Optional approval delegation

## Validation Rules

1. **Address Validation**: Must be 42-character hex string starting with 0x
2. **Amount Validation**: Must be positive number or "unlimited"
3. **Strategy Validation**: Must be one of: unlimited, exact, increase, safe
4. **Action Validation**: Must be one of: check, approve, revoke, batch_check
5. **Batch Size**: Maximum 50 spenders per batch_check

## Security Considerations

1. **Risk Levels**: 
   - Low: Known protocol, reasonable amount, temporary approval
   - Medium: Unknown spender, high amount
   - High: Unlimited approval, suspicious spender, emergency alert

2. **Risk Flags**:
   - Unlimited approvals with no expiration
   - Unknown/suspicious spender contracts
   - Approval amount exceeds available balance
   - Repeated approvals to same spender

3. **Best Practices**:
   - Use exact amount instead of unlimited when possible
   - Revoke unused approvals regularly
   - Check spender before approving
   - Use safe strategy for critical tokens

## Performance

- **Response Time**: < 2 seconds per check
- **Batch Operations**: < 5 seconds for 50 spenders
- **Gas Estimation**: Included in approval/revoke operations
- **Rate Limits**: No application-level limits

## Supported Networks

Currently supports Ethereum mainnet. Future versions may add:
- Polygon
- Arbitrum
- Optimism
- Base
- Other EVM chains

## Testing

### Test Cases Included
- ✅ USDC allowance check (mainnet data)
- ✅ Approval with exact amount strategy
- ✅ Revoke allowance operation
- ✅ Batch check multiple spenders
- ✅ Risk assessment for unlimited approvals
- ✅ Known spender identification
- ✅ Error handling for invalid addresses

### Example Test
```bash
echo '{
  "owner": "0x1234567890123456789012345678901234567890",
  "spender": "0x68b3465833fb72B5A828cCEEB955439B22B36987",
  "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "action": "check"
}' | python3 scripts/main.py
```

## Version History

- **v1.0.0** (Feb 2026)
  - Initial release with web3.py RPC integration
  - Support for check, approve, revoke, batch_check actions
  - Real blockchain queries instead of simulator
  - Known spender identification
  - Risk assessment framework

## Author
web3devzz

## License
MIT

## Related Skills
- wallet-multisend - Multi-recipient token transfers
- token-liquidity-scan - Liquidity pool analysis
- erc20-transfer-monitor - Token transfer tracking
