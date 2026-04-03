# ERC20 Allowance Manager

Check, approve, revoke, and manage ERC20 token allowances with multiple approval strategies and security analysis.

## Features
- **Check Allowance**: View current approved amount for specific spender
- **Approve Token**: Set allowance with 4 strategies (unlimited, exact, increase, safe)
- **Revoke Allowance**: Set allowance to zero in single transaction
- **Batch Queries**: Check allowances for multiple spenders in one call
- **Known Spenders**: Identifies popular protocols (Uniswap, 1inch, OpenSea, etc.)
- **Risk Assessment**: Flags unlimited approvals and low-balance dangers
- **Token Registry**: 5+ verified tokens with proper decimal handling
- **Approval Strategies**: Safe pattern, unlimited, exact amount, increase existing

## Usage

### Check Allowance
```bash
echo '{
  "owner": "0x1234567890123456789012345678901234567890",
  "spender": "0x68b3465833fb72B5A828cCEEB955439B22B36987",
  "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "action": "check"
}' | python3 scripts/main.py
```

### Approve with Exact Amount
```bash
echo '{
  "owner": "0x1234567890123456789012345678901234567890",
  "spender": "0x68b3465833fb72B5A828cCEEB955439B22B36987",
  "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "action": "approve",
  "amount": "1000.00",
  "strategy": "exact"
}' | python3 scripts/main.py
```

### Approve with Unlimited Strategy
```bash
echo '{
  "owner": "0x1234567890123456789012345678901234567890",
  "spender": "0x68b3465833fb72B5A828cCEEB955439B22B36987",
  "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "action": "approve",
  "strategy": "unlimited"
}' | python3 scripts/main.py
```

### Revoke Allowance
```bash
echo '{
  "owner": "0x1234567890123456789012345678901234567890",
  "spender": "0x68b3465833fb72B5A828cCEEB955439B22B36987",
  "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "action": "revoke"
}' | python3 scripts/main.py
```

### Batch Check Multiple Spenders
```bash
echo '{
  "owner": "0x1234567890123456789012345678901234567890",
  "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "action": "batch_check",
  "spenders": [
    "0x68b3465833fb72B5A828cCEEB955439B22B36987",
    "0x1111111254fb6c44bac0bed2854e76f90643097d",
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
  ]
}' | python3 scripts/main.py
```

## Parameters

### Common
- `owner` (required): Token owner address
- `token` (required): ERC20 token address
- `action` (optional): Action to perform (check, approve, revoke, batch_check) - default: check

### For check/approve/revoke
- `spender` (required): Spender contract address

### For approve
- `amount` (optional): Amount to approve (for exact/increase strategies)
- `strategy` (optional): Approval strategy (unlimited, exact, increase, safe) - default: exact

### For batch_check
- `spenders` (required): Array of spender addresses (max 50)

## Response
Returns allowance details, spender identification, approval risk assessment, and transaction information.

## RPC Blockchain Integration

### Simulator Mode (Default)
By default, the tool runs in simulator mode using hard-coded token registries and pre-populated allowance caches. This allows full functionality without requiring an RPC node:

```bash
echo '{"owner": "0x1234...","spender": "0x68b3...","token": "0xa0b8...","action": "check"}' | python3 scripts/main.py
# Returns: {"success": true, "source": "simulator", ...}
```

### Real Blockchain Mode with RPC
To read actual allowances from the Ethereum blockchain, set an RPC endpoint and install web3.py:

```bash
pip install web3
export ETH_RPC_URL="https://eth.llamarpc.com"
```

Then the tool automatically fetches real data:

```bash
echo '{"owner": "0x1234...","spender": "0x68b3...","token": "0xa0b8...","action": "check"}' | python3 scripts/main.py
# Returns: {"success": true, "source": "blockchain_rpc", ...}
```

### RPC Endpoint Examples
- **Infura**: `https://mainnet.infura.io/v3/YOUR_PROJECT_ID`
- **Alchemy**: `https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY`
- **Public LlamaRPC**: `https://eth.llamarpc.com`
- **Local Node**: `http://localhost:8545`

### RPC Fallback Behavior
If RPC is configured but connection fails, the tool automatically falls back to simulator mode with a warning printed to stderr. This ensures robustness in production environments.

### Configuring RPC Per Request
You can also pass RPC URL in the request itself:

```bash
echo '{
  "owner": "0x1234...",
  "token": "0xa0b8...",
  "spender": "0x68b3...",
  "rpc_url": "https://eth.llamarpc.com",
  "action": "check"
}' | python3 scripts/main.py
```
