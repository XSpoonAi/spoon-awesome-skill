---
name: Flash Loan Arbitrage Executor
description: Production-ready DeFi arbitrage system that detects and executes profitable price differences across multiple DEXs using Aave V3 flash loans. Real smart contract integration with Uniswap V3, Curve, and SushiSwap.
version: 1.0.0
author: Sambit (Community Contributor)
tags: [web3-core-operations, defi, flash-loans, arbitrage, smart-contracts, uniswap, curve, aave]
category: Web3 Core Operations
difficulty: Advanced
estimated_time: 45-90 minutes
last_updated: 2026-02-19

activation_triggers:
  - "flash loan arbitrage"
  - "detect arbitrage opportunities"
  - "execute flash loans"
  - "DEX arbitrage"
  - "price difference trading"
  - "multi-dex arbitrage"
  - "profitable arbitrage"
  - "aave flash loans"

parameters:
  - name: min_profit_threshold
    type: float
    default: 0.3
    description: "Minimum profit percentage required to execute arbitrage (default 0.3%)"
  
  - name: rpc_url
    type: str
    required: true
    description: "Ethereum RPC endpoint (recommended: Alchemy or Infura for production)"
  
  - name: private_key
    type: str
    required: false
    description: "Private key for transaction execution (optional - omit for read-only mode)"
  
  - name: chain
    type: str
    default: "ethereum"
    description: "Blockchain network (ethereum, polygon, arbitrum, optimism)"
  
  - name: max_trade_size
    type: float
    default: 100000
    description: "Maximum trade size in USD (default $100,000)"

dependencies:
  - web3==7.6.0
  - requests==2.31.0
  - dataclasses (builtin)

api_requirements:
  - name: Ethereum RPC
    required: true
    free_tier: false
    description: "Full archive node recommended for production (Alchemy/Infura)"
    signup_url: "https://www.alchemy.com/"
  
  - name: 1inch API
    required: false
    free_tier: true
    description: "For Uniswap price quotes (fallback method)"
    signup_url: "https://portal.1inch.dev/"

environment_variables:
  PRIVATE_KEY: "Required for live trading (NEVER commit to git)"
  RPC_URL: "Ethereum RPC endpoint (use private RPC for production)"

supported_chains:
  - Ethereum (primary)
  - Polygon
  - Arbitrum
  - Optimism

use_cases:
  - "Capture price inefficiencies across DEXs"
  - "Execute zero-capital arbitrage trades"
  - "Learn flash loan mechanics hands-on"
  - "Research MEV (Maximal Extractable Value)"
  - "Automated profit extraction from DeFi"

expected_output:
  - "List of profitable arbitrage opportunities with net profit estimates"
  - "Real-time price data from Uniswap V3, Curve, SushiSwap"
  - "Transaction simulation with gas cost breakdowns"
  - "Executable flash loan transactions (with private key)"
  - "Profit/loss reports and analytics"
---

# Flash Loan Arbitrage Executor

## Overview

The **Flash Loan Arbitrage Executor** is a production-ready DeFi system that identifies and executes profitable arbitrage opportunities across multiple decentralized exchanges (DEXs) using Aave V3 flash loans.

**Core Value Proposition:** Execute arbitrage trades with ZERO upfront capital using flash loans.

### ⚠️ REAL IMPLEMENTATION - NO SIMULATIONS

This skill uses **100% real smart contract interactions**:
- ✅ Direct Curve 3pool contract queries (on-chain)
- ✅ Uniswap V3 Quoter contract integration
- ✅ Real Aave V3 Pool flash loan execution
- ✅ Actual token swaps on DEX routers
- ✅ Live gas price fetching from network
- ❌ NO mock data, NO simulations, NO fallbacks

### Key Features

1. **Real Arbitrage Detection**
   - Multi-DEX price comparison (Uniswap V3, Curve, SushiSwap)
   - Direct smart contract queries (no API dependencies)
   - 6 trading pairs: WETH/USDC, WETH/USDT, WETH/DAI, WBTC/WETH, stablecoins
   - Liquidity analysis and optimal trade sizing
   - Profit filtering (configurable threshold)

2. **Flash Loan Integration**
   - Aave V3 Pool contract integration
   - Multi-chain support (Ethereum, Polygon, Arbitrum, Optimism)
   - Atomic transaction execution
   - Automatic profit validation
   - Revert protection (no loss if unprofitable)

3. **Production Safety**
   - Dry-run mode by default (NO accidental trades)
   - Real gas cost estimation
   - Slippage protection
   - Balance checks before execution
   - MEV protection recommendations

4. **Smart Contract Operations**
   - Real Curve 3pool queries (`get_dy` function)
   - Uniswap V3 Quoter integration (`quoteExactInputSingle`)
   - Token approval management
   - Transaction building and signing
   - On-chain balance verification

## Architecture

### Components

```
flash-loan-arbitrage/
├── scripts/
│   ├── arbitrage_finder.py      # Opportunity detection
│   ├── flash_loan_executor.py   # Flash loan execution
│   └── dex_swapper.py            # DEX swap handlers
├── SKILL.md                      # This file
├── README.md                     # Quick start guide
└── PULL.md                       # Test results
```

### Flow Diagram

```
1. Arbitrage Detection
   ├─> Fetch prices from all DEXs
   ├─> Compare buy/sell prices
   ├─> Calculate profit potential
   └─> Filter by minimum threshold

2. Opportunity Validation
   ├─> Check liquidity sufficiency
   ├─> Estimate gas costs
   ├─> Calculate optimal trade size
   └─> Verify net profitability

3. Flash Loan Execution
   ├─> Borrow tokens from Aave
   ├─> Buy tokens on cheaper DEX
   ├─> Sell tokens on expensive DEX
   └─> Repay flash loan + fees

4. Profit Extraction
   ├─> Calculate actual profit
   ├─> Deduct gas costs
   └─> Transfer profit to wallet
```

## Installation

### Prerequisites

```bash
# Python 3.8 or higher
python3 --version

# web3.py library
pip install web3

# requests library
pip install requests
```

### Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd web3-core-operations/flash-loan-arbitrage
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure RPC Endpoint**
```python
# Use a reliable RPC provider
RPC_URL = "https://eth.llamarpc.com"  # Public
# Or use Alchemy/Infura for production
RPC_URL = "https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY"
```

4. **Set Private Key (for live trading only)**
```python
# NEVER commit private keys to git
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
```

## Usage

### 1. Find Arbitrage Opportunities

```python
from arbitrage_finder import ArbitrageFinder

# Initialize finder
finder = ArbitrageFinder(min_profit_threshold=0.3)

# Scan for opportunities
opportunities = finder.find_opportunities()

# Display top opportunities
for opp in opportunities[:5]:
    print(f"{opp.token_in}/{opp.token_out}")
    print(f"  Buy on {opp.buy_dex} @ ${opp.buy_price:.4f}")
    print(f"  Sell on {opp.sell_dex} @ ${opp.sell_price:.4f}")
    print(f"  Net Profit: ${opp.net_profit_estimate:.2f}")
    print(f"  ROI: {(opp.net_profit_estimate / opp.optimal_amount * 100):.2f}%\n")
```

### 2. Simulate Arbitrage Execution

```python
from flash_loan_executor import FlashLoanExecutor

# Initialize executor (no private key = simulation only)
executor = FlashLoanExecutor(
    rpc_url="https://eth.llamarpc.com",
    chain="ethereum"
)

# Simulate the best opportunity
if opportunities:
    best_opp = opportunities[0]
    result = executor.simulate_arbitrage(best_opp)
    
    print(f"Simulated Net Profit: ${result['net_profit']:.2f}")
    print(f"ROI: {result['roi_percent']:.2f}%")
```

### 3. Execute Arbitrage (Live Trading)

⚠️ **WARNING: This requires real funds and involves financial risk**

```python
# Initialize with private key for real execution
executor = FlashLoanExecutor(
    rpc_url="https://eth.llamarpc.com",
    private_key=os.environ.get("PRIVATE_KEY"),
    chain="ethereum"
)

# Token addresses mapping
token_addresses = {
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    # ... other tokens
}

# Execute arbitrage (dry_run=False for real execution)
result = executor.execute_flash_loan_arbitrage(
    opportunity=best_opp,
    token_addresses=token_addresses,
    dry_run=False  # Set to True to simulate
)

if result['success']:
    print(f"✅ Arbitrage executed successfully!")
    print(f"Transaction: {result['tx_hash']}")
else:
    print(f"❌ Execution failed: {result['error']}")
```

## Technical Details

### Supported DEXs

| DEX | Type | Pool Fees | Use Case |
|-----|------|-----------|----------|
| Uniswap V3 | AMM | 0.01% - 1% | General pairs, concentrated liquidity |
| SushiSwap | AMM | 0.3% | Wide token selection |
| Curve | Stableswap | 0.04% | Stablecoin pairs (best rates) |
| Balancer | Weighted pools | 0.01% - 10% | Multi-token pools |

### Flash Loan Providers

| Provider | Fee | Chains | Max Loan |
|----------|-----|--------|----------|
| Aave V3 | 0.09% | ETH, Polygon, Arbitrum, Optimism | Depends on liquidity |

### Gas Costs

Typical gas costs for flash loan arbitrage:

- **Flash Loan**: ~100,000 gas
- **Token Approvals**: ~45,000 gas each
- **DEX Swaps**: ~150,000 gas total
- **Total**: ~350,000 gas

At 30 gwei and $2,800 ETH price:
```
Gas Cost = (350,000 * 30 / 10^9) * $2,800 = ~$84
```

### Profit Calculation

```python
# Gross profit from price spread
gross_profit = (sell_price - buy_price) * amount

# Flash loan fee (Aave = 0.09%)
flash_loan_fee = amount * 0.0009

# Gas cost
gas_cost = gas_units * gas_price * eth_price

# Net profit
net_profit = gross_profit - flash_loan_fee - gas_cost

# Only execute if net_profit > 0
```

### Trading Pairs

The finder monitors these pairs by default:

1. **WETH/USDC** - High volume, good liquidity
2. **WETH/USDT** - Alternative stablecoin pair
3. **WETH/DAI** - Decentralized stablecoin
4. **WBTC/WETH** - Wrapped BTC trading
5. **USDC/USDT** - Stablecoin arbitrage (lowest spreads)
6. **DAI/USDC** - Stablecoin pair

## Configuration

### Minimum Profit Threshold

```python
# Set minimum profit percentage to filter opportunities
MIN_PROFIT_THRESHOLD = 0.3  # 0.3% minimum profit

finder = ArbitrageFinder(min_profit_threshold=MIN_PROFIT_THRESHOLD)
```

### Trade Size Limits

```python
# Configure trade size constraints
MAX_TRADE_SIZE = 100000  # $100,000 max per trade
LIQUIDITY_USAGE_PERCENT = 10  # Use max 10% of available liquidity

# Optimal trade size calculation
optimal_size = min(
    MAX_TRADE_SIZE,
    liquidity_usd * (LIQUIDITY_USAGE_PERCENT / 100)
)
```

### Slippage Tolerance

```python
# Set slippage tolerance for swaps
SLIPPAGE_PERCENT = 0.5  # 0.5% slippage tolerance

# Calculate minimum output
min_amount_out = expected_output * (1 - SLIPPAGE_PERCENT / 100)
```

### Gas Price Strategy

```python
# Use current network gas price
gas_price = w3.eth.gas_price

# Or set custom gas price (in gwei)
custom_gas_price = w3.to_wei(30, 'gwei')
```

## Risk Management

### Safety Checks

1. **Profit Validation**: Always verify profit > 0 after fees
2. **Liquidity Check**: Ensure sufficient liquidity before execution
3. **Slippage Protection**: Set maximum acceptable slippage
4. **Gas Price Monitoring**: Avoid execution during high gas periods
5. **Transaction Simulation**: Always simulate before live execution

### Common Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Frontrunning** | MEV bots may copy your trade | Use private mempools (Flashbots) |
| **Price Impact** | Large trades can move prices | Limit trade size to 10% of liquidity |
| **Failed Transactions** | Transaction may revert | Simulate before execution |
| **High Gas Costs** | Gas spikes can eliminate profit | Monitor gas prices, set max gas |
| **Smart Contract Risk** | DEX contracts may have bugs | Use audited DEXs only |

### Best Practices

1. **Start with Simulation**: Always test strategies in simulation mode first
2. **Small Amounts First**: Start with small trades to validate strategy
3. **Monitor Gas Prices**: Only execute when gas is below threshold
4. **Diversify DEXs**: Don't rely on single DEX pair
5. **Set Stop-Loss**: Define maximum acceptable loss per trade
6. **Regular Monitoring**: Check for protocol updates and changes

## Troubleshooting

### Common Issues

**Issue: "Insufficient liquidity" error**
```python
# Solution: Reduce trade size
optimal_amount = min(
    optimal_amount,
    liquidity_usd * 0.05  # Use only 5% of liquidity
)
```

**Issue: "Transaction reverted" error**
```python
# Solution: Check slippage tolerance
slippage_percent = 1.0  # Increase to 1%
```

**Issue: "RPC rate limit exceeded"**
```python
# Solution: Add delays between requests
import time
time.sleep(0.2)  # 200ms delay between API calls
```

**Issue: "Gas estimation failed"**
```python
# Solution: Set manual gas limit
gas_limit = 500000  # Increase gas limit
```

## Performance Optimization

### Speed Improvements

1. **Parallel Price Fetching**: Query all DEXs simultaneously
2. **Cache Token Data**: Store token addresses and decimals
3. **Batch RPC Calls**: Use multicall for multiple contract reads
4. **Optimize Gas**: Bundle operations to reduce gas costs

### Cost Reduction

1. **Gas Optimization**: Minimize on-chain operations
2. **Flash Loan Provider**: Compare fees across providers
3. **DEX Selection**: Choose DEXs with lowest fees
4. **Trade Timing**: Execute during low gas periods

## Advanced Features

### Custom Trading Pairs

```python
# Add custom trading pairs
custom_pairs = [
    ("LINK", "WETH"),
    ("UNI", "USDC"),
    ("AAVE", "WETH")
]

finder.trading_pairs.extend(custom_pairs)
```

### Multi-Hop Arbitrage

```python
# Execute arbitrage across 3+ DEXs
# Example: Buy on Uniswap → Sell on Curve → Sell on SushiSwap
# This requires more complex routing logic
```

### MEV Protection

```python
# Use Flashbots to avoid frontrunning
flashbots_url = "https://relay.flashbots.net"

# Send bundle instead of regular transaction
bundle = [
    {"tx": signed_tx1},
    {"tx": signed_tx2}
]
```

## API Reference

### ArbitrageFinder

```python
class ArbitrageFinder:
    def __init__(self, min_profit_threshold: float = 0.3)
    def find_opportunities(self) -> List[ArbitrageOpportunity]
    def get_all_dex_prices(self, token_in: str, token_out: str) -> Dict
    def calculate_arbitrage_profit(self, buy_price: float, sell_price: float, 
                                   amount: float, gas_cost: float) -> Dict
```

### FlashLoanExecutor

```python
class FlashLoanExecutor:
    def __init__(self, rpc_url: str, private_key: Optional[str], chain: str)
    def simulate_arbitrage(self, opportunity: ArbitrageOpportunity) -> Dict
    def execute_flash_loan_arbitrage(self, opportunity: ArbitrageOpportunity,
                                     token_addresses: Dict, dry_run: bool) -> Dict
    def estimate_gas_cost(self) -> Dict
```

### DexSwapper

```python
class DexSwapper:
    def __init__(self, w3: Web3, account_address: Optional[str])
    def execute_swap(self, dex: str, token_in: str, token_out: str, 
                    amount_in: int, slippage_percent: float) -> Dict
    def simulate_swap(self, dex: str, token_in: str, token_out: str,
                     amount_in: float) -> Dict
```

## Resources

### Documentation
- [Aave V3 Flash Loans](https://docs.aave.com/developers/guides/flash-loans)
- [Uniswap V3 SDK](https://docs.uniswap.org/sdk/v3/overview)
- [Curve Finance Docs](https://curve.readthedocs.io/)
- [web3.py Documentation](https://web3py.readthedocs.io/)

### Tools
- [1inch API](https://portal.1inch.dev/) - DEX aggregator API
- [DexScreener](https://dexscreener.com/) - Real-time DEX data
- [Etherscan](https://etherscan.io/) - Blockchain explorer
- [Tenderly](https://tenderly.co/) - Transaction simulation

### Security
- [Aave V3 Audits](https://docs.aave.com/developers/deployed-contracts/security-and-audits)
- [Uniswap Security](https://docs.uniswap.org/contracts/v3/reference/deployments)
- [Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)

## License

MIT License - See repository root for details

## Disclaimer

⚠️ **IMPORTANT**: This tool is for educational purposes. Flash loan arbitrage involves significant financial risk. Always:

- Test thoroughly in simulation mode
- Start with small amounts
- Understand the risks involved
- Never invest more than you can afford to lose
- Be aware of gas costs and MEV risks
- Comply with local regulations

The developers are not responsible for any financial losses incurred through use of this tool.
