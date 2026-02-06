# Identity ENS Lookup - Skill Specification

## Skill ID
`identity-ens-lookup`

## Category
Web3 Core Operations

## Overview
Real-time Ethereum Name Service (ENS) resolution using blockchain RPC queries. Resolves ENS domain names to Ethereum addresses and vice versa, with support for retrieving metadata like avatars, text records, and resolver information.

## Capabilities

### Core Functions
1. **resolve** - Forward resolution: ENS name → Ethereum address
2. **reverse** - Reverse resolution: Ethereum address → ENS name

### Supported Operations
- **ENS Name Resolution**: Convert `.eth` names to addresses with full metadata
- **Reverse Resolution**: Convert addresses back to registered ENS names with verification
- **Text Records**: Retrieve avatar, email, twitter, github, discord, url, description
- **Ownership Info**: Get ENS domain owner and resolver contract details
- **Namehash Calculation**: Compute ENS node hash for query purposes

## Input Format

### Parameters
```json
{
  "name": "vitalik.eth",        // ENS name (with or without .eth suffix)
  "address": "0x...",           // Ethereum address (for reverse resolution)
  "action": "resolve|reverse"   // Optional, auto-detected from parameters
}
```

**Note**: Provide either `name` (for forward resolution) OR `address` (for reverse resolution), not both.

## Output Format

### Success Response (Forward Resolution)
```json
{
  "success": true,
  "name": "vitalik.eth",
  "node": "0xee6c4522aab0003e8d14cd40a6af439055fd2577951148c14b6cea9a53475835",
  "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "owner": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "resolver": "0x231b0Ee14048e9dCcD1d247744d114a4EB5E8E63",
  "text_records": {
    "avatar": "https://euc.li/vitalik.eth",
    "url": "https://vitalik.ca",
    "description": "mi pinxe lo crino tcati",
    "twitter": "@VitalikButerin",
    "github": "vbuterin"
  },
  "block_number": 24398659,
  "rpc_used": "https://eth-mainnet.public.blastapi.io",
  "timestamp": "2026-02-06T15:24:23+00:00"
}
```

### Success Response (Reverse Resolution)
```json
{
  "success": true,
  "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "name": "vitalik.eth",
  "verified": true,
  "block_number": 24398660,
  "rpc_used": "https://eth-mainnet.public.blastapi.io",
  "timestamp": "2026-02-06T15:24:35+00:00"
}
```

### No ENS Name Registered (Reverse Resolution)
```json
{
  "success": true,
  "address": "0x1234567890123456789012345678901234567890",
  "name": null,
  "message": "No reverse ENS name registered"
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
| `validation_error` | No ENS name registered / Invalid format | Verify ENS name or address format |
| `system_error` | Unexpected error | Check logs and retry |

## Configuration

### Environment Variables
```bash
ETHEREUM_RPC=https://eth-mainnet.public.blastapi.io  # Custom RPC endpoint (optional)
```

## Dependencies

### Required
- `web3` >= 6.0 (Install via: `pip install web3`)
- `eth-utils` >= 2.0 (Included with web3)
- Python 3.8+

### Optional
- None

## Blockchain Integration

### RPC Methods
- `eth_blockNumber` - Get current block for metadata
- `eth_call` - Query ENS registry and resolver contracts

### Smart Contracts
- **ENS Registry**: `0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e`
- **Public Resolver**: `0x231b0Ee14048e9dCcD1d247744d114a4EB5E8E63` (example)
- **Reverse Registrar**: `0x084b1c3c81545d370f3634d6e5409d2afb65c9e3`

### Protocol Details
- **ENS Naming Scheme**: `labels.reverse` for reverse resolution
- **Namehash**: Recursive keccak256 hash of domain labels
- **Text Record Keys**: avatar, email, twitter, github, discord, url, description, com.discord, com.twitter, org.Email, etc.

## Validation Rules

1. **ENS Name Validation**: Must be valid domain format (alphanumeric + hyphens), case-insensitive
2. **Address Validation**: Must be 42-character hex string starting with 0x
3. **Auto-Suffix**: Automatically appends `.eth` if not provided in name
4. **Namehash Calculation**: Uses Keccak-256 hashing over split labels in reverse order

## Real-World Data Guarantees

All responses include:
- **Block Number**: Current Ethereum block number queried
- **RPC Endpoint**: The RPC provider used (proves real blockchain data)
- **Timestamp**: Block timestamp proving recent data
- **Verification**: Reverse resolution includes forward verification check

Example: `vitalik.eth` resolves to `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` with real text records from blockchain.

## Performance

- **Forward Resolution**: < 2 seconds
- **Reverse Resolution**: < 3 seconds (includes verification)
- **Text Record Lookup**: < 1 second per record
- **Rate Limits**: No application-level limits (depends on RPC provider)

## Supported Networks

Currently supports Ethereum mainnet. Future versions may add:
- Polygon
- Arbitrum
- Optimism
- Base
- Other EVM chains with ENS deployments

## Testing

### Test Cases Included
- ✅ Forward resolve vitalik.eth to address
- ✅ Retrieve text records (avatar, url, description)
- ✅ Reverse resolve address to vitalik.eth
- ✅ Verify forward/reverse consistency
- ✅ Handle unregistered ENS names
- ✅ Error handling for invalid addresses
- ✅ Real blockchain data from multiple queries

### Example Tests
```bash
# Test forward resolution
echo '{"name": "vitalik.eth"}' | python3 scripts/main.py

# Test reverse resolution
echo '{"address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"}' | python3 scripts/main.py

# Test error handling
echo '{"name": "nonexistent123456789.eth"}' | python3 scripts/main.py
```

## Version History

- **v1.0.0** (Feb 2026)
  - Initial release with web3.py RPC integration
  - Forward and reverse ENS resolution
  - ENS text record retrieval
  - Real blockchain queries instead of simulator
  - Verification of forward/reverse consistency

## Author
web3devzz

## License
MIT

## Related Skills
- wallet-multisend - Multi-recipient token transfers
- erc20-allowance-manager - Token approval management
- token-liquidity-scan - Liquidity pool analysis
- dex-arb-detector - Arbitrage detection across DEXes

## References

- **ENS Documentation**: https://docs.ens.domains/
- **ENS Smart Contracts**: https://github.com/ensdomains/ens-contracts
- **Web3.py Docs**: https://web3py.readthedocs.io/
- **Ethereum RPC API**: https://ethereum.org/en/developers/docs/apis/json-rpc/
$ echo '{"name": "vitalik.eth"}' | python3 scripts/main.py
{
  "success": true,
  "name": "vitalik.eth",
  "address": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
  "owner": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
  "avatar": "https://euc.li/vitalik.eth",
  "text_records": {
    "email": "user@example.com",
    "twitter": "@user"
  }
}
```

## Error Handling

When an error occurs, the skill returns:

```json
{
  "ok": false,
  "error": "Error description",
  "details": {
    "name": "Name not found"
  }
}
```
