# Gas Optimizer

Production-ready gas optimization toolkit for Ethereum and Layer 2 networks. Analyze costs, batch transactions, and save up to 99% on gas fees by choosing the right network and strategy.

## Features

### 🔍 Real-Time Gas Monitoring
- Live gas prices from Etherscan API
- EIP-1559 base fee + priority fee tracking
- Network congestion analysis
- Historical gas price trends

### 💰 Cost Estimation
- Accurate transaction cost calculation via Web3 RPC
- USD conversion with real-time ETH prices
- Multiple gas speed options (safe, standard, fast)
- Custom transaction type support

### 📦 Transaction Batching
- Multicall3 integration for gas savings
- Batch multiple calls into single transaction
- 25-35% gas reduction on average
- Support for token approvals, swaps, and custom calls

### 🌐 Multi-Chain Comparison
- Compare costs across 6 networks:
  - Ethereum Mainnet
  - Arbitrum One
  - Optimism
  - Polygon
  - Base
  - zkSync Era
- Real-time L1/L2 cost analysis
- Bridge cost estimation
- Up to 99.9% savings on L2

### 🎯 Smart Strategies
- Urgency-based gas recommendations
- Transaction type optimization
- Off-peak scheduling suggestions
- MEV protection guidance

## Installation

```bash
# Clone repository
git clone https://github.com/XSpoonAI/spoon-awesome-skill.git
cd spoon-awesome-skill/web3-core-operations/gas-optimizer

# Install dependencies
pip install web3 requests eth-abi eth-utils

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with the following:

```env
# Required
ETHERSCAN_API_KEY=your_etherscan_api_key_here
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_key

# Optional (for multi-chain)
INFURA_KEY=your_infura_key_here
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
OPTIMISM_RPC_URL=https://mainnet.optimism.io
```

### Get API Keys (Free)

1. **Etherscan API** (required)
   - Sign up at https://etherscan.io/apis
   - Free tier: 5 calls/second
   - Used for gas price data

2. **Alchemy/Infura** (required for RPC)
   - Alchemy: https://www.alchemy.com/
   - Infura: https://infura.io/
   - Free tier: 100k requests/day
   - Used for transaction estimation

3. **CoinGecko** (optional)
   - Auto-used for price data
   - No API key needed for basic use

## Usage Examples

### 1. Get Current Gas Prices

```python
from scripts.gas_estimator import GasEstimator

estimator = GasEstimator()

# Get real-time gas prices
prices = estimator.get_current_gas_prices()
print(f"Safe: {prices['gas_prices']['safe']} Gwei")
print(f"Standard: {prices['gas_prices']['proposed']} Gwei")
print(f"Fast: {prices['gas_prices']['fast']} Gwei")
```

Output:
```
Safe: 25.5 Gwei
Standard: 28.0 Gwei
Fast: 32.5 Gwei
Network Congestion: medium
```

### 2. Estimate Transaction Cost

```python
# Estimate cost for Uniswap swap
cost = estimator.estimate_transaction_cost(
    to_address="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    data="0xa9059cbb...",  # Your transaction data
    value=0
)

print(f"Gas Estimate: {cost['gas_estimate']} units")
print(f"Cost (Safe): ${cost['costs']['safe_gas']['total_cost_usd']}")
print(f"Cost (Fast): ${cost['costs']['fast_gas']['total_cost_usd']}")
```

Output:
```
Gas Estimate: 150000 units
Cost (Safe): $9.56
Cost (Fast): $12.19
```

### 3. Batch Transactions with Multicall

```python
from scripts.transaction_batcher import TransactionBatcher

batcher = TransactionBatcher()

# Prepare multiple token approvals
transactions = [
    {
        "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        "data": "0x095ea7b3...",  # approve() call
        "value": 0
    },
    {
        "to": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
        "data": "0x095ea7b3...",
        "value": 0
    },
    {
        "to": "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
        "data": "0x095ea7b3...",
        "value": 0
    }
]

# Batch into single transaction
result = batcher.batch_transactions(transactions, chain_id=1)

print(f"Transactions batched: {result['transactions_batched']}")
print(f"Individual gas: {result['gas_estimates']['individual_total']}")
print(f"Batched gas: {result['gas_estimates']['batched']}")
print(f"Savings: {result['gas_estimates']['savings_percentage']}%")
```

Output:
```
Transactions batched: 3
Individual gas: 195000
Batched gas: 135000
Savings: 30.77%
```

### 4. Compare L2 Networks

```python
from scripts.l2_comparison import L2GasComparison

l2_comp = L2GasComparison()

# Compare swap costs across networks
comparison = l2_comp.compare_transaction_costs(
    transaction_type='swap',
    networks=['ethereum', 'arbitrum', 'optimism', 'polygon']
)

print("\nNetwork Cost Comparison:")
for network in comparison['comparison']:
    print(f"{network['network']}: ${network['total_cost_usd']}")
    print(f"  Savings: {network['savings_percentage']}%")
```

Output:
```
Network Cost Comparison:
Polygon: $0.01 (Savings: 99.92%)
Arbitrum One: $0.23 (Savings: 98.17%)
Optimism: $0.35 (Savings: 97.20%)
Ethereum Mainnet: $10.50 (Savings: 0.00%)
```

### 5. Get Smart Gas Strategy

```python
from scripts.gas_optimizer import GasOptimizer

optimizer = GasOptimizer()

# Get recommendation for DeFi swap
strategy = optimizer.suggest_optimal_gas_strategy(
    transaction_type='swap',
    urgency='medium'
)

print(f"Recommended Gas Price: {strategy['recommended_strategy']['total_gas_price_gwei']} Gwei")
print(f"Estimated Cost: ${strategy['recommended_strategy']['estimated_cost_eth']} ETH")
print(f"Wait Time: {strategy['recommended_strategy']['estimated_wait_time']}")
print("\nRecommendations:")
for rec in strategy['recommendations']:
    print(f"  - {rec}")
```

Output:
```
Recommended Gas Price: 32.2 Gwei
Estimated Cost: 0.004833 ETH
Wait Time: 3-5 minutes

Recommendations:
  - Consider using Layer 2 solutions (Arbitrum, Optimism) for 95% gas savings
  - Schedule transaction during off-peak hours (weekends, early UTC morning)
```

### 6. Analyze Historical Transactions

```python
# Analyze wallet's transaction patterns
analysis = optimizer.analyze_transaction_pattern(
    address="0x28C6c06298d514Db089934071355E5743bf21d60",
    num_transactions=100
)

print(f"Transactions Analyzed: {analysis['transactions_analyzed']}")
print(f"Average Gas Used: {analysis['statistics']['average_gas_used']}")
print(f"Failed Transactions: {analysis['statistics']['failed_transactions']}")
print(f"\nOptimization Opportunities:")
for opt in analysis['optimizations']:
    print(f"  - {opt['description']}")
    print(f"    Estimated Savings: {opt.get('estimated_savings', 0)} gas")
```

Output:
```
Transactions Analyzed: 100
Average Gas Used: 125000
Failed Transactions: 3

Optimization Opportunities:
  - 87 contract interactions detected
    Estimated Savings: 32625 gas
  - Gas prices range from 18.50 to 85.20 Gwei
    Estimated Savings: 8337 gas
```

### 7. Estimate Bridge Costs

```python
# Calculate cost to bridge from Ethereum to Arbitrum
bridge_cost = l2_comp.get_bridge_costs(
    from_network='ethereum',
    to_network='arbitrum',
    amount_usd=1000.0
)

print(f"Bridge Route: {bridge_cost['route']['from']} → {bridge_cost['route']['to']}")
print(f"Amount: ${bridge_cost['amount_usd']}")
print(f"Total Cost: ${bridge_cost['costs']['total_cost_usd']}")
print(f"Fee Percentage: {bridge_cost['costs']['total_fee_percentage']}%")
print(f"Estimated Time: {bridge_cost['estimated_time']}")
```

Output:
```
Bridge Route: Ethereum Mainnet → Arbitrum One
Amount: $1000.0
Total Cost: $14.40
Fee Percentage: 1.44%
Estimated Time: 10-15 minutes
```

## Advanced Usage

### Custom Contract Optimization

```python
# Analyze specific contract call
optimization = optimizer.optimize_contract_call(
    contract_address="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",  # UNI token
    function_signature="transfer(address,uint256)",
    params=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", 1000000]
)

print(f"Estimated Gas: {optimization['analysis']['estimated_gas']}")
print(f"Complexity: {optimization['analysis']['complexity_level']}")
print(f"\nOptimizations:")
for opt in optimization['optimizations']:
    print(f"  {opt['type']}: {opt['description']}")
    print(f"  Priority: {opt['priority']}")
    print(f"  Savings: {opt['potential_saving_gas']} gas")
```

### Token Approval Batching

```python
# Batch approve multiple tokens for Uniswap router
tokens = [
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
    "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
    "0x6B175474E89094C44Da98b954EedeAC495271d0F"   # DAI
]

result = batcher.create_token_approval_batch(
    token_addresses=tokens,
    spender="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap Router
    amount=2**256 - 1,  # Unlimited approval
    chain_id=1
)

print(f"Batched {len(tokens)} approvals")
print(f"Gas savings: {result['gas_estimates']['savings_percentage']}%")
```

## Transaction Types

The optimizer supports various transaction types:

| Type | Base Gas | Description |
|------|----------|-------------|
| `transfer` | 21,000 | Simple ETH transfer |
| `erc20_transfer` | 65,000 | Token transfer |
| `swap` | 150,000 | DEX swap (Uniswap, etc.) |
| `mint` | 100,000 | NFT minting |
| `stake` | 120,000 | Token staking |
| `complex_defi` | 300,000 | Complex DeFi operations |

## Urgency Levels

| Level | Description | Wait Time | Use Case |
|-------|-------------|-----------|----------|
| `low` | Off-peak gas prices | 10-30 min | Non-urgent transfers |
| `medium` | Standard confirmation | 3-5 min | Regular transactions |
| `high` | Fast confirmation | < 2 min | Time-sensitive swaps |
| `urgent` | Next block | < 30 sec | Liquidation protection |

## Supported Networks

| Network | Chain ID | Type | Typical Gas Cost |
|---------|----------|------|------------------|
| Ethereum | 1 | L1 | $5-50 |
| Arbitrum | 42161 | L2-Optimistic | $0.10-1 |
| Optimism | 10 | L2-Optimistic | $0.20-2 |
| Polygon | 137 | Sidechain | $0.01-0.10 |
| Base | 8453 | L2-Optimistic | $0.10-1 |
| zkSync Era | 324 | L2-ZK | $0.20-2 |

## Best Practices

### 1. Gas Price Monitoring
- Check gas prices during off-peak hours (weekends, early UTC)
- Use `low` urgency for non-critical transactions
- Set up alerts for gas price thresholds

### 2. Transaction Batching
- Batch approvals before swaps
- Combine multiple operations into single Multicall
- Use `allow_failure=true` for non-critical batch items

### 3. Network Selection
- Use L2 for frequent small transactions
- Bridge during low gas periods
- Consider transaction urgency vs cost

### 4. Gas Strategy
- Use EIP-1559 with dynamic fees
- Simulate transactions before sending
- Monitor mempool for stuck transactions

## Error Handling

All functions return structured responses:

```python
{
    "success": true/false,
    "error": "Error message if failed",
    ...data
}
```

Always check the `success` field:

```python
result = estimator.get_current_gas_prices()
if not result['success']:
    print(f"Error: {result['error']}")
else:
    # Process data
    pass
```

## Troubleshooting

### API Rate Limits
```
Error: "Max rate limit reached"
Solution: Upgrade Etherscan API tier or add rate limiting
```

### RPC Connection Issues
```
Error: "Failed to connect to RPC"
Solution: Check ETHEREUM_RPC_URL or use alternative provider
```

### Invalid Transaction Data
```
Error: "Invalid transaction data"
Solution: Ensure data is hex string starting with '0x'
```

## Performance

- Average response time: < 2 seconds
- API calls per transaction estimate: 2-3
- Batch size limit: 50 transactions (Multicall3)
- Historical analysis: 100 transactions in ~5 seconds

## Security Considerations

- Never commit `.env` file with API keys
- Use environment variables for sensitive data
- Validate all transaction data before sending
- Test on testnet first
- Use Flashbots for MEV-sensitive transactions

## Contributing

This skill is part of the Spoon Awesome Skills repository. Contributions are welcome!

## License

MIT License - see repository root for details

## Support

- Documentation: See `SKILL.md` for detailed specifications
- Issues: https://github.com/XSpoonAI/spoon-awesome-skill/issues
- Discord: Join SpoonOS community

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** SpoonOS Team
