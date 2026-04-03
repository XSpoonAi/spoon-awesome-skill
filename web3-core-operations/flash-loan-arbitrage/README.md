# Flash Loan Arbitrage Executor

> Identify and execute profitable arbitrage opportunities across multiple DEXs using Aave flash loans

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd web3-core-operations/flash-loan-arbitrage

# Install dependencies
pip install web3 requests
```

### Basic Usage

```python
from scripts.arbitrage_finder import ArbitrageFinder
from scripts.flash_loan_executor import FlashLoanExecutor

# 1. Find opportunities
finder = ArbitrageFinder(min_profit_threshold=0.3)
opportunities = finder.find_opportunities()

print(f"Found {len(opportunities)} profitable opportunities")

# 2. Simulate best opportunity
if opportunities:
    best = opportunities[0]
    print(f"\nBest Opportunity:")
    print(f"  Pair: {best.token_in}/{best.token_out}")
    print(f"  Buy: {best.buy_dex} @ ${best.buy_price:.4f}")
    print(f"  Sell: {best.sell_dex} @ ${best.sell_price:.4f}")
    print(f"  Profit: ${best.net_profit_estimate:.2f}")
    
    # 3. Simulate execution
    executor = FlashLoanExecutor(
        rpc_url="https://eth.llamarpc.com",
        chain="ethereum"
    )
    
    result = executor.simulate_arbitrage(best)
    print(f"\nSimulation Result:")
    print(f"  Net Profit: ${result['net_profit']:.2f}")
    print(f"  ROI: {result['roi_percent']:.2f}%")
```

## How It Works

### 1. Opportunity Detection

The `arbitrage_finder.py` module scans multiple DEXs for price discrepancies:

```
Uniswap: USDC/USDT = 1.0005
Curve:   USDC/USDT = 0.9995
         ↓
Price Gap = 0.1% → Potential Profit!
```

### 2. Profit Calculation

```
Trade Amount:     $10,000
Price Spread:      0.1%
Gross Profit:     $100
Flash Loan Fee:   -$9 (0.09%)
Gas Cost:         -$84
Net Profit:       $7
```

### 3. Flash Loan Execution

```
1. Borrow $10,000 USDC from Aave (flash loan)
2. Buy USDT on Curve at 0.9995 (cheaper)
3. Sell USDT on Uniswap at 1.0005 (expensive)
4. Repay $10,009 to Aave ($10,000 + 0.09% fee)
5. Keep profit in wallet
```

All in **one atomic transaction** - either everything succeeds or everything reverts!

## Features

✅ **Multi-DEX Support**: Uniswap V3, SushiSwap, Curve, Balancer  
✅ **Real-Time Pricing**: Live price feeds from DEX APIs  
✅ **Profit Filtering**: Only shows profitable opportunities  
✅ **Gas Optimization**: Accurate gas cost estimates  
✅ **Simulation Mode**: Test without risking funds  
✅ **Multi-Chain**: Ethereum, Polygon, Arbitrum, Optimism

## Supported Trading Pairs

- 🔷 **WETH/USDC** - High volume
- 🔷 **WETH/USDT** - Alternative stablecoin
- 🔷 **WETH/DAI** - Decentralized stablecoin
- 🔷 **WBTC/WETH** - Wrapped BTC
- 🔷 **USDC/USDT** - Stablecoin arbitrage
- 🔷 **DAI/USDC** - Low volatility

## Configuration

### Minimum Profit Threshold

```python
# Only show opportunities with at least 0.3% profit
finder = ArbitrageFinder(min_profit_threshold=0.3)
```

### RPC Endpoint

```python
# Use public RPC (rate limited)
RPC_URL = "https://eth.llamarpc.com"

# Or use private RPC (recommended for production)
RPC_URL = "https://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY"
```

### Gas Price Limits

```python
# Current gas price
gas_price = w3.eth.gas_price

# Check gas before executing
if gas_price > w3.to_wei(50, 'gwei'):
    print("Gas too high, waiting...")
```

## Example Output

```
🔍 Scanning for arbitrage opportunities...

💰 OPPORTUNITY #1
   Pair: USDC/USDT
   Buy on curve @ $0.9995
   Sell on uniswap @ $1.0005
   Price Gap: 0.60%
   Optimal Amount: $20,000.00
   Gross Profit: $120.00
   Gas Cost: $84.00
   Flash Loan Fee: $18.00
   Net Profit: $18.00
   ROI: 0.09%

💰 OPPORTUNITY #2
   Pair: WETH/USDC
   Buy on sushiswap @ $2,799.50
   Sell on uniswap @ $2,801.25
   Price Gap: 1.75%
   Optimal Amount: $50,000.00
   Gross Profit: $875.00
   Gas Cost: $84.00
   Flash Loan Fee: $45.00
   Net Profit: $746.00
   ROI: 1.49%

Found 2 profitable opportunities
```

## Live Trading (Advanced)

⚠️ **WARNING**: Live trading requires real funds and involves financial risk!

```python
import os
from scripts.flash_loan_executor import FlashLoanExecutor

# Set private key via environment variable
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")

# Initialize executor with private key
executor = FlashLoanExecutor(
    rpc_url="https://eth.llamarpc.com",
    private_key=PRIVATE_KEY,
    chain="ethereum"
)

# Token addresses
token_addresses = {
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
}

# Execute arbitrage (dry_run=False for real execution)
result = executor.execute_flash_loan_arbitrage(
    opportunity=opportunities[0],
    token_addresses=token_addresses,
    dry_run=False  # ⚠️ This will execute a real transaction!
)

if result['success']:
    print(f"✅ Arbitrage executed!")
    print(f"   Transaction: https://etherscan.io/tx/{result['tx_hash']}")
    print(f"   Gas Used: {result['gas_used']}")
else:
    print(f"❌ Execution failed: {result['error']}")
```

## Safety Features

### Simulation Mode (Default)

All execution is simulated by default - no real transactions sent:

```python
# This will NOT send a real transaction
result = executor.simulate_arbitrage(opportunity)
```

### Dry Run Mode

Even with private key, you can test safely:

```python
# This will prepare transaction but NOT send it
result = executor.execute_flash_loan_arbitrage(
    opportunity=opp,
    token_addresses=tokens,
    dry_run=True  # Safe mode
)
```

### Profit Verification

The executor automatically:
- ✅ Validates profit > 0 after all fees
- ✅ Checks liquidity sufficiency
- ✅ Estimates gas costs accurately
- ✅ Reverts transaction if unprofitable

### Slippage Protection

```python
# Set maximum acceptable slippage
swapper.execute_swap(
    dex="uniswap",
    token_in="USDC",
    token_out="USDT",
    amount_in=10000,
    slippage_percent=0.5  # 0.5% max slippage
)
```

## Gas Cost Estimates

Typical flash loan arbitrage gas usage:

| Operation | Gas Units | Cost @ 30 gwei |
|-----------|-----------|----------------|
| Flash Loan | ~100,000 | ~$8.40 |
| DEX Swap 1 | ~150,000 | ~$12.60 |
| DEX Swap 2 | ~150,000 | ~$12.60 |
| **Total** | **~400,000** | **~$33.60** |

*Based on $2,800 ETH price*

## Common Issues

### "Insufficient liquidity"

**Solution**: Reduce trade size

```python
# Use smaller percentage of available liquidity
optimal_amount = min(
    optimal_amount,
    liquidity_usd * 0.05  # Only use 5% of liquidity
)
```

### "Transaction reverted"

**Solution**: Increase slippage tolerance

```python
slippage_percent = 1.0  # Increase to 1%
```

### "No opportunities found"

**Solution**: Lower profit threshold

```python
finder = ArbitrageFinder(min_profit_threshold=0.1)  # Lower to 0.1%
```

### "RPC rate limit exceeded"

**Solution**: Use private RPC endpoint

```python
# Get free API key from Alchemy or Infura
RPC_URL = "https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY"
```

## Risk Disclaimer

⚠️ **IMPORTANT SAFETY NOTICE**

Flash loan arbitrage involves significant risks:

- **Financial Loss**: You can lose money due to gas costs, failed transactions, or market movements
- **Front-Running**: MEV bots may copy your profitable trades
- **Smart Contract Risk**: DEX or flash loan contracts may have vulnerabilities
- **Regulatory Risk**: Check local regulations regarding DeFi trading
- **Market Risk**: Prices can change rapidly, eliminating profit opportunities

**Always:**
- ✅ Test thoroughly in simulation mode first
- ✅ Start with small amounts
- ✅ Monitor gas prices
- ✅ Understand the risks
- ✅ Never invest more than you can afford to lose

## Performance Tips

### 1. Use Private RPC

Public RPCs are rate-limited. Use Alchemy or Infura for production:

```python
RPC_URL = "https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY"
```

### 2. Monitor Gas Prices

Don't execute during gas spikes:

```python
gas_price = w3.eth.gas_price
if gas_price < w3.to_wei(30, 'gwei'):
    # Good time to execute
    executor.execute_flash_loan_arbitrage(...)
```

### 3. Parallel Price Fetching

The finder queries multiple DEXs simultaneously for speed:

```python
# Automatically fetches prices in parallel
prices = finder.get_all_dex_prices("WETH", "USDC")
```

### 4. Focus on Liquid Pairs

More liquidity = better execution:

```python
# WETH/USDC typically has $50M+ liquidity
# USDC/USDT has $100M+ liquidity on Curve
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Arbitrage Finder                        │
│  - Scans DEX prices                                      │
│  - Calculates profit                                     │
│  - Filters opportunities                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Flash Loan Executor                         │
│  - Simulates execution                                   │
│  - Estimates gas                                         │
│  - Executes atomic transaction                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                 DEX Swapper                              │
│  - Handles Uniswap swaps                                 │
│  - Handles Curve swaps                                   │
│  - Manages token approvals                               │
└─────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Read SKILL.md**: Comprehensive technical documentation
2. **Test in Simulation**: Run `arbitrage_finder.py` to scan opportunities
3. **Analyze Results**: Review profitable opportunities and understand profit sources
4. **Small Test Trade**: Execute with minimum amount first
5. **Monitor & Optimize**: Track performance and adjust parameters

## Resources

- 📚 [SKILL.md](SKILL.md) - Detailed technical documentation
- 📊 [PULL.md](PULL.md) - Test results and benchmarks
- 🔗 [Aave V3 Docs](https://docs.aave.com/developers/guides/flash-loans)
- 🔗 [Uniswap V3 Docs](https://docs.uniswap.org/)
- 🔗 [Curve Finance](https://curve.readthedocs.io/)

## Support

For questions or issues:
1. Check [SKILL.md](SKILL.md) for detailed documentation
2. Review [PULL.md](PULL.md) for example test cases
3. Open an issue in the repository

## License

MIT License - See repository root for details

---

**Built with ❤️ for the DeFi community**
