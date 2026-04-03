# EVM Transaction Debugger

**Debug failed EVM transactions in seconds -- decode reverts, profile gas, parse events, and get actionable fixes across 7 chains. No API keys required.**

## Why EVM Transaction Debugger?

Debugging failed blockchain transactions is painful. Error messages are cryptic hex strings, gas analysis requires manual calculation, and event logs are raw binary data. This skill automates the entire debugging workflow.

### Feature Comparison

| Feature | EVM TX Debugger | Tenderly | Etherscan | Manual |
|---------|----------------|----------|-----------|--------|
| Revert reason decoding | Yes (auto) | Yes (paid) | Partial | Manual ABI lookup |
| Custom error decoding | Yes | Yes (paid) | No | Very difficult |
| Gas efficiency scoring | Yes (0-100) | Basic | Gas used only | Manual math |
| EIP-1559 breakdown | Yes | Yes | Partial | Manual |
| Event log parsing | Yes (auto) | Yes (paid) | Raw only | Manual ABI lookup |
| Multi-chain support | 7 chains | 20+ chains | Per-site | N/A |
| API key required | No | Yes | Yes (rate limits) | N/A |
| Natural language output | Yes | No | No | No |
| Actionable fix suggestions | Yes | No | No | No |
| Cost | Free | $49+/mo | Free (limited) | Time |
| AI-integrated | SpoonOS native | No | No | No |

## Quick Start

### Debug a Failed Transaction
```
"Debug this failed transaction: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
```

### Analyze Gas on a Specific Chain
```
"Analyze gas usage for 0xabcdef... on polygon"
```

### Parse Transaction Events
```
"Parse events from tx 0xfedcba... on arbitrum"
```

## Architecture

```
evm-tx-debugger/
├── SKILL.md              # Skill definition with triggers and parameters
├── README.md             # This file
└── scripts/
    ├── tx_decoder.py      # Transaction input data decoder
    ├── error_classifier.py # Failure classification and revert decoding
    ├── gas_profiler.py     # Gas usage analysis and efficiency scoring
    └── event_parser.py     # Event log parsing and interpretation
```

### Data Flow

```
User Query (tx_hash + chain)
    │
    ├──> tx_decoder.py ──> Decoded method, params, addresses
    ├──> error_classifier.py ──> Error type, revert reason, fixes
    ├──> gas_profiler.py ──> Gas metrics, efficiency score
    └──> event_parser.py ──> Decoded events, human descriptions
    │
    └──> Combined Debug Report
```

## Scripts

### tx_decoder.py -- Transaction Decoder

Decodes a transaction's input data to reveal the method called, its parameters, and execution context.

**APIs Used:**
- Blockscout `/api/v2/transactions/{hash}` -- transaction details
- 4byte.directory `/api/v1/signatures/` -- method selector lookup

**Input JSON:**
```json
{
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
  "chain": "ethereum"
}
```

**Output JSON:**
```json
{
  "success": true,
  "scan_type": "transaction_decode",
  "transaction": {
    "hash": "0x1234...",
    "chain": "ethereum",
    "chain_id": "1",
    "block_number": 18500000,
    "timestamp": "2024-01-15T12:30:00Z",
    "status": "ok",
    "is_success": true
  },
  "from_address": "0xSender...",
  "to_address": "0xContract...",
  "value_wei": "0",
  "value_eth": "0.0",
  "method": {
    "selector": "0x38ed1739",
    "name": "swapExactTokensForTokens",
    "signature": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
    "decoded_inputs": "0x38ed1739 -> swapExactTokensForTokens (via 4byte.directory)"
  },
  "gas": {
    "gas_used": "152340",
    "gas_limit": "300000",
    "gas_price": "25000000000"
  },
  "contract_interaction": {
    "is_contract_call": true,
    "contract_name": "UniswapV2Router02",
    "contract_verified": true
  }
}
```

**Key Features:**
- Automatic method selector resolution via 4byte.directory
- Contract name and verification status from Blockscout
- EIP-1559 field support (maxFeePerGas, maxPriorityFeePerGas)
- Raw input data extraction for unresolved selectors

---

### error_classifier.py -- Error Classifier

Classifies transaction failures, decodes revert reasons, and provides human-readable explanations with suggested fixes.

**APIs Used:**
- Blockscout `/api/v2/transactions/{hash}` -- status and revert reason
- 4byte.directory `/api/v1/signatures/` -- custom error selector decoding

**Input JSON:**
```json
{
  "tx_hash": "0xfailed_tx_hash...",
  "chain": "ethereum"
}
```

**Output JSON:**
```json
{
  "success": true,
  "scan_type": "error_classification",
  "transaction": {
    "hash": "0xfailed...",
    "chain": "ethereum",
    "status": "error",
    "is_success": false
  },
  "error": {
    "classification": "REVERT",
    "raw_revert_reason": "0x08c379a0....",
    "decoded_reason": "UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT",
    "error_selector": "0x08c379a0",
    "error_type": "Error(string)"
  },
  "explanation": {
    "summary": "The transaction was reverted by the contract because the output token amount was less than the minimum specified.",
    "common_causes": [
      "Price moved unfavorably between submission and execution",
      "Slippage tolerance set too low",
      "Insufficient liquidity in the pool"
    ],
    "suggested_fixes": [
      "Increase slippage tolerance (e.g., from 0.5% to 1-3%)",
      "Use a smaller trade size to reduce price impact",
      "Check if the token has transfer taxes that affect output amount",
      "Try again when network is less congested"
    ]
  },
  "risk_assessment": {
    "score": 2,
    "level": "LOW"
  }
}
```

**Error Classification Table:**

| Classification | Description | Severity |
|---------------|-------------|----------|
| OUT_OF_GAS | Transaction ran out of gas during execution | MEDIUM |
| REVERT | Contract explicitly reverted execution | LOW-HIGH |
| INSUFFICIENT_FUNDS | Sender balance too low | LOW |
| NONCE_TOO_LOW | Transaction nonce already used | LOW |
| CONTRACT_CREATION_FAILED | Contract deployment failed | HIGH |
| INVALID_OPCODE | Invalid EVM instruction executed | HIGH |
| STACK_OVERFLOW | EVM stack depth exceeded | HIGH |
| UNKNOWN | Unrecognized failure mode | MEDIUM |

---

### gas_profiler.py -- Gas Profiler

Profiles gas consumption, calculates efficiency metrics, and compares usage against network averages.

**APIs Used:**
- Blockscout `/api/v2/transactions/{hash}` -- gas metrics
- Blockscout `/api/v2/stats` -- network average statistics

**Input JSON:**
```json
{
  "tx_hash": "0x1234...",
  "chain": "ethereum"
}
```

**Output JSON:**
```json
{
  "success": true,
  "scan_type": "gas_profile",
  "transaction": {
    "hash": "0x1234...",
    "chain": "ethereum",
    "status": "ok"
  },
  "gas_metrics": {
    "gas_used": 152340,
    "gas_limit": 300000,
    "gas_price_gwei": 25.0,
    "effective_gas_price_gwei": 24.5,
    "efficiency_percent": 50.78,
    "gas_wasted": 147660
  },
  "eip1559": {
    "is_eip1559": true,
    "max_fee_per_gas_gwei": 30.0,
    "max_priority_fee_per_gas_gwei": 2.0,
    "base_fee_per_gas_gwei": 22.5,
    "priority_fee_savings_gwei": 5.5
  },
  "cost": {
    "total_cost_eth": 0.003733,
    "total_cost_usd": 6.72,
    "cost_at_gas_limit_eth": 0.00735,
    "savings_eth": 0.003617
  },
  "network_comparison": {
    "network_avg_gas_price_gwei": 20.0,
    "price_vs_average": "25% above average",
    "network_avg_gas_used": 21000,
    "usage_vs_average": "7.25x average (complex contract interaction)"
  },
  "efficiency_score": {
    "score": 51,
    "grade": "C",
    "assessment": "Gas limit was set too high. Consider reducing gas limit closer to actual usage.",
    "recommendations": [
      "Reduce gas limit to ~190,000 (1.25x actual usage)",
      "Gas price was 25% above network average"
    ]
  }
}
```

**Efficiency Score Grading:**

| Score | Grade | Assessment |
|-------|-------|------------|
| 90-100 | A | Excellent -- gas limit well-calibrated |
| 75-89 | B | Good -- minor optimization possible |
| 50-74 | C | Fair -- gas limit too generous |
| 25-49 | D | Poor -- significant gas wasted |
| 0-24 | F | Very poor -- extreme over-allocation |

---

### event_parser.py -- Event Parser

Parses transaction event logs, decodes them using known signatures and 4byte.directory, and provides human-readable descriptions.

**APIs Used:**
- Blockscout `/api/v2/transactions/{hash}/logs` -- raw event logs
- 4byte.directory `/api/v1/event-signatures/` -- event name lookup

**Input JSON:**
```json
{
  "tx_hash": "0x1234...",
  "chain": "ethereum"
}
```

**Output JSON:**
```json
{
  "success": true,
  "scan_type": "event_parse",
  "transaction": {
    "hash": "0x1234...",
    "chain": "ethereum",
    "status": "ok"
  },
  "events": {
    "total": 3,
    "decoded": 3,
    "unresolved": 0
  },
  "parsed_events": [
    {
      "index": 0,
      "event_name": "Transfer",
      "signature": "Transfer(address,address,uint256)",
      "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "contract_name": "USDC",
      "topics": ["0xddf252ad...", "0x000...sender", "0x000...receiver"],
      "decoded_params": {
        "from": "0xSender...",
        "to": "0xReceiver...",
        "value": "1000000"
      },
      "description": "Transferred 1,000,000 units from 0xSender to 0xReceiver"
    }
  ],
  "event_summary": [
    "1. Transfer: 1,000,000 USDC from 0xSender to 0xReceiver",
    "2. Approval: 0xOwner approved 0xSpender for unlimited WETH",
    "3. Swap: Swapped 1.5 ETH for 2,700 USDC on Uniswap V2"
  ]
}
```

**Common Event Signatures Recognized:**

| Event | Signature | Protocol |
|-------|-----------|----------|
| Transfer | `Transfer(address,address,uint256)` | ERC-20/721 |
| Approval | `Approval(address,address,uint256)` | ERC-20/721 |
| TransferSingle | `TransferSingle(address,address,address,uint256,uint256)` | ERC-1155 |
| Swap (V2) | `Swap(address,uint256,uint256,uint256,uint256,address)` | Uniswap V2 |
| Swap (V3) | `Swap(address,address,int256,int256,uint160,uint128,int24)` | Uniswap V3 |
| Deposit | `Deposit(address,uint256)` | WETH |
| Withdrawal | `Withdrawal(address,uint256)` | WETH |
| OwnershipTransferred | `OwnershipTransferred(address,address)` | OpenZeppelin |

## Composability

The EVM Transaction Debugger is designed to work alongside other SpoonOS skills:

### With Smart Contract Auditor
```
1. Debug a failed transaction -> identify the contract that reverted
2. Feed the contract address to Smart Contract Auditor for a full security audit
3. Combine findings: "Transaction failed because contract has reentrancy vulnerability"
```

### With DeFi Safety Shield
```
1. Parse events from a suspicious transaction
2. Feed token addresses from Transfer events to DeFi Safety Shield
3. Determine if failed transaction was due to interacting with a malicious token
```

### With Crypto Market Intelligence
```
1. Profile gas costs for a transaction
2. Use market data to calculate accurate USD cost at time of transaction
3. Compare gas efficiency across different chains for the same operation
```

## API Reference

All APIs are free, require no authentication, and have generous rate limits.

| API | Base URL | Purpose | Rate Limit |
|-----|----------|---------|------------|
| Blockscout | `https://{chain}.blockscout.com` | Transaction data, logs, stats | ~5 req/s |
| 4byte.directory | `https://www.4byte.directory/api/v1` | Method/event selector decoding | ~10 req/s |

### Blockscout Chain Endpoints

| Chain | Endpoint |
|-------|----------|
| Ethereum | `https://eth.blockscout.com` |
| BSC | `https://bsc.blockscout.com` |
| Polygon | `https://polygon.blockscout.com` |
| Arbitrum | `https://arbitrum.blockscout.com` |
| Base | `https://base.blockscout.com` |
| Optimism | `https://optimism.blockscout.com` |
| Avalanche | `https://avax.blockscout.com` |

## Use Cases

### 1. Failed DEX Swap
A user's Uniswap swap failed with a cryptic revert. The debugger decodes the revert reason as `INSUFFICIENT_OUTPUT_AMOUNT`, explains that price slippage exceeded the tolerance, and suggests increasing slippage or reducing trade size.

### 2. Out-of-Gas Contract Deployment
A developer's contract deployment failed with out-of-gas. The gas profiler shows the deployment consumed 100% of the gas limit, recommends increasing the gas limit by 20-50%, and flags the contract size as unusually large.

### 3. NFT Mint Failure
An NFT mint transaction reverts with a custom error. The error classifier decodes the custom error selector, identifies it as `MintExceedsMaxSupply()`, and explains the collection has reached its maximum supply.

### 4. Bridge Transaction Analysis
A cross-chain bridge transaction emits multiple events. The event parser decodes each event in sequence, showing the token lock on the source chain, the message relay, and providing a clear narrative of the bridge flow.

### 5. Gas Optimization Audit
A protocol team wants to optimize their smart contract's gas usage. The gas profiler analyzes multiple transactions, calculates efficiency scores, and identifies patterns where gas limits are consistently over-allocated.

### 6. MEV Attack Investigation
A trader suspects their transaction was sandwich attacked. The event parser decodes all events in the block, revealing a frontrun buy and backrun sell around the victim's swap, with the debugger calculating the exact profit extracted.

## Error Handling

All scripts return consistent error JSON on failure:

```json
{
  "success": false,
  "error": "Description of what went wrong",
  "error_type": "VALIDATION_ERROR | API_ERROR | PARSE_ERROR",
  "suggestion": "How to fix the issue"
}
```

### Common Error Responses

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid tx_hash format` | Hash not 0x + 64 hex chars | Check transaction hash format |
| `Unsupported chain` | Chain name not recognized | Use: ethereum, bsc, polygon, arbitrum, base, optimism, avalanche |
| `Transaction not found` | Hash not on specified chain | Verify the chain parameter matches where the tx was sent |
| `Rate limit exceeded` | Too many API requests | Wait a moment and retry (auto-retry built in) |

## Technical Details

- **Python**: 3.8+ compatible
- **Dependencies**: Standard library only (`json`, `sys`, `urllib`, `re`, `time`)
- **I/O**: JSON via stdin/stdout
- **Timeout**: 30 seconds per script
- **Retry Logic**: Exponential backoff on HTTP 429 (rate limit)
- **Validation**: Strict tx_hash and chain validation before API calls

## Supported Transaction Types

| Type | Decode | Error Analysis | Gas Profile | Events |
|------|--------|----------------|-------------|--------|
| ETH Transfer | Yes | Yes | Yes | N/A |
| ERC-20 Transfer | Yes | Yes | Yes | Yes |
| ERC-721 Transfer | Yes | Yes | Yes | Yes |
| DEX Swap | Yes | Yes | Yes | Yes |
| Contract Deploy | Yes | Yes | Yes | Yes |
| Contract Call | Yes | Yes | Yes | Yes |
| Multi-call | Yes | Yes | Yes | Yes |
| Proxy Call | Yes | Yes | Yes | Yes |

## License

MIT License. Free to use, modify, and distribute.
