---
name: Gas Optimizer
description: Advanced gas optimization tool for Ethereum and EVM-compatible chains. Analyzes transactions, simulates gas usage, suggests optimal gas prices, batches transactions, and implements gas-saving patterns for smart contract interactions.
version: 1.0.0
author: Web3 Builder
tags:
  - gas-optimization
  - ethereum
  - evm
  - transaction-optimization
  - cost-reduction
  - web3
  - blockchain
  - layer2

activation_triggers:
  - keyword: "optimize gas"
  - keyword: "gas price"
  - keyword: "transaction cost"
  - pattern: "gas_estimation|fee_optimization|batch_transactions"
  - intent: "reduce_transaction_costs"

parameters:
  - name: transaction_data
    type: object
    required: true
    description: "Transaction details to optimize (to, data, value)"
    example: {"to": "0x...", "data": "0x...", "value": "0"}
  
  - name: chain_id
    type: integer
    required: true
    description: "Chain ID (1=Ethereum, 137=Polygon, 42161=Arbitrum)"
    example: 1
  
  - name: optimization_level
    type: string
    required: false
    enum: ["fast", "standard", "economical"]
    default: "standard"
    description: "Gas optimization strategy"
    example: "economical"
  
  - name: max_gas_price_gwei
    type: number
    required: false
    description: "Maximum acceptable gas price in Gwei"
    example: 50

scripts:
  - name: gas_estimator
    type: python
    path: scripts/gas_estimator.py
    description: "Estimates gas costs and suggests optimal gas prices"
    confidence: "95%"
    params: ["transaction_data", "chain_id"]
  
  - name: transaction_batcher
    type: python
    path: scripts/transaction_batcher.py
    description: "Batches multiple transactions to save gas"
    confidence: "93%"
    params: ["transaction_data", "optimization_level"]
  
  - name: gas_tracker
    type: python
    path: scripts/gas_tracker.py
    description: "Real-time gas price tracking and prediction"
    confidence: "91%"
    params: ["chain_id"]
  
  - name: pattern_optimizer
    type: python
    path: scripts/pattern_optimizer.py
    description: "Suggests gas-efficient code patterns"
    confidence: "89%"
    params: ["transaction_data"]

capabilities:
  - Real-time gas price tracking (Ethereum, Polygon, Arbitrum, Optimism, BSC)
  - Transaction gas estimation with 95% accuracy
  - Optimal gas price suggestion (fast/standard/economical)
  - Transaction batching and bundling
  - EIP-1559 fee optimization (base fee + priority fee)
  - Layer 2 cost comparison
  - Gas-efficient pattern recommendations
  - Historical gas price analysis
  - Gas cost forecasting
  - Multi-signature transaction optimization
  - Contract deployment cost estimation
  - Storage optimization suggestions

cache: true
composable: true

security_considerations:
  - Never expose private keys
  - Validate all transaction data before signing
  - Implement slippage protection
  - Use secure RPC endpoints
  - Verify gas estimates before execution
  - Implement maximum gas price limits
  - Monitor for front-running attacks
  - Use multicall for batch transactions safely
---

## Usage Examples

### Estimate Gas Cost
```python
from scripts.gas_estimator import GasEstimator

estimator = GasEstimator()
estimate = estimator.estimate_gas(
    transaction={"to": "0x...", "data": "0x..."},
    chain_id=1
)
print(f"Estimated gas: {estimate['gas_limit']} units")
print(f"Cost: ${estimate['cost_usd']}")
```

### Get Optimal Gas Price
```python
from scripts.gas_tracker import GasTracker

tracker = GasTracker()
prices = tracker.get_gas_prices(chain_id=1)
print(f"Fast: {prices['fast']} Gwei")
print(f"Standard: {prices['standard']} Gwei")
print(f"Economical: {prices['economical']} Gwei")
```

### Batch Transactions
```python
from scripts.transaction_batcher import TransactionBatcher

batcher = TransactionBatcher()
batched = batcher.batch_transactions([
    {"to": "0x...", "data": "0x..."},
    {"to": "0x...", "data": "0x..."}
])
print(f"Gas savings: {batched['gas_saved_percentage']}%")
```

### Optimize Contract Patterns
```python
from scripts.pattern_optimizer import PatternOptimizer

optimizer = PatternOptimizer()
suggestions = optimizer.analyze_contract("contract_code.sol")
print(f"Potential savings: {suggestions['estimated_savings']} gas")
```

## Output Format

All modules return structured JSON:

```json
{
  "chain_id": number,
  "gas_estimate": number,
  "gas_price_gwei": number,
  "cost_eth": string,
  "cost_usd": string,
  "optimization_level": "string",
  "gas_saved": number,
  "recommendations": ["array"],
  "execution_time": "string"
}
```

## Severity Levels

| Level | Meaning | Impact | Action |
|-------|---------|--------|--------|
| CRITICAL | Unsafe transaction or gas price spike | High risk | Wait or cancel |
| HIGH | Inefficient gas usage detected | Moderate cost | Optimize before sending |
| MEDIUM | Better timing available | Low-moderate cost | Consider waiting |
| LOW | Minor optimization possible | Low cost | Optional improvement |

## Version & Support

- **Version**: 1.0.0
- **Released**: February 2026
- **Status**: Production Ready
- **Confidence**: 92%


---
