---
name: Whale Wallet Copier
description: Identifies wallets that achieved >100% APY in the last month and alerts you when they buy new tokens. Complete intelligence system for copy trading high-performing whales.
version: 1.0.0
author: Sambit (Community Contributor)
tags: [web3-data-intelligence, onchain-analysis, whale-tracking, copy-trading, trading-signals]
category: Web3 Data Intelligence
difficulty: Advanced
estimated_time: 30-60 minutes
last_updated: 2026-02-19

activation_triggers:
  - "identify whale wallets"
  - "find high performing traders"
  - "copy trade whales"
  - "track whale purchases"
  - "alert on whale buys"
  - "whale wallet analysis"
  - "calculate wallet APY"
  - "monitor successful traders"

parameters:
  - name: wallet_addresses
    type: List[str] 
    required: true
    description: "List of wallet addresses to screen for whale performance"
  
  - name: min_apy
    type: float
    default: 100
    description: "Minimum APY threshold to qualify as a whale (default 100%)"
  
  - name: days_back
    type: int
    default: 30
    description: "Time period for performance analysis (default 30 days)"
  
  - name: check_interval
    type: int
    default: 60
    description: "Seconds between transaction checks when monitoring (default 60s)"
  
  - name: monitor_duration
    type: int
    default: 1440
    description: "How long to monitor whale wallets in minutes (default 24 hours)"

dependencies:
  - requests==2.31.0
  - datetime (builtin)
  - typing (builtin)

api_requirements:
  - name: Etherscan API
    required: false
    free_tier: true
    description: "For fetching wallet transactions (5 calls/sec free tier)"
    signup_url: "https://etherscan.io/apis"
  
  - name: DexScreener API
    required: false
    free_tier: true
    description: "For token prices and analysis (300 calls/min free tier)"
    signup_url: "https://dexscreener.com"

environment_variables:
  ETHERSCAN_API_KEY: "Optional - for higher rate limits (free tier: YourApiKeyToken)"

supported_chains:
  - Ethereum (primary)
  - BSC (via Etherscan-like APIs)
  - Polygon (via Etherscan-like APIs)
  - Arbitrum (via Etherscan-like APIs)

use_cases:
  - "Copy trade high-performing wallets automatically"
  - "Early detection of promising tokens before they pump"
  - "Whale activity intelligence and insights"
  - "Portfolio strategy research and analysis"
  - "Real-time trading signals from successful traders"

expected_output:
  - "List of whale wallets with >100% APY" 
  - "Real-time alerts when whales buy new tokens"
  - "Token analysis (price, liquidity, safety score)"
  - "Actionable trading signals with confidence ratings"
  - "Performance reports and analytics"
---

# Whale Wallet Copier (Trading Intelligence)

## Overview

The **Whale Wallet Copier** is a comprehensive on-chain intelligence system that identifies high-performing Ethereum wallets (>100% APY) and monitors their transactions in real-time to generate actionable trading signals.

**Core Value Proposition:** Know what successful traders are buying *before* the market does.

### Key Features

1. **Performance Tracking** - Calculate wallet APY from transaction history
2. **Whale Discovery** - Screen thousands of wallets to find top performers
3. **Real-Time Monitoring** - Track whale purchases as they happen
4. **Token Analysis** - Evaluate safety, liquidity, and potential of purchased tokens
5. **Trading Signals** - Get actionable alerts with complete context

### Problem Solved

**Challenge:** Retail traders lack the tools and intelligence that institutional players use to identify profitable opportunities early.

**Solution:** By tracking wallets that have proven track records (>100% APY), you can copy their strategy and catch winning tokens at the same time they do.

**Real-World Impact:**
- **Early Entry:** Buy tokens within minutes of whale purchases
- **Proven Strategy:** Follow wallets with verified performance, not random influencers
- **Risk Management:** Automatic token safety analysis filters scams
- **Data-Driven:** Decisions based on on-chain data, not speculation

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│              Whale Wallet Copier System                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─ 1. DISCOVERY PHASE
                              │  └─ whale_performance_tracker.py
                              │     - Fetch wallet transactions
                              │     - Calculate cost basis & current value
                              │     - Compute APY over time periods
                              │     - Identify whales (>100% APY)
                              │
                              ├─ 2. MONITORING PHASE
                              │  └─ transaction_monitor.py
                              │     - Poll whale wallets for new txs
                              │     - Detect token purchases
                              │     - Filter spam & stablecoins
                              │     - Get token analysis (DexScreener)
                              │
                              └─ 3. ORCHESTRATION & ALERTS
                                 └─ whale_alerter.py
                                    - Coordinate discovery → monitoring
                                    - Generate real-time alerts
                                    - Save signals & reports
                                    - Provide actionable intelligence
```

### Data Flow

```
Wallet List → Screen for Performance → Identify Whales (>100% APY)
                                             ↓
                                    Monitor Transactions
                                             ↓
                                    Detect New Purchases
                                             ↓
                                    Analyze Token Safety
                                             ↓
                                    Generate Trading Signal
                                             ↓
                                    Alert User (Buy Signal)
```

---

## Installation

### Prerequisites

- Python 3.10+
- Active internet connection
- Etherscan API key (optional, free tier available)

### Setup

```bash
# Navigate to skill directory
cd web3-data-intelligence/whale-wallet-copier

# Install dependencies
pip install requests

# Optional: Set Etherscan API key for higher rate limits
export ETHERSCAN_API_KEY="your_api_key_here"

# Test installation
python scripts/whale_alerter.py
```

---

## Usage

### Quick Start - Full Workflow

```python
from scripts.whale_alerter import WhaleWalletCopier

# Initialize
copier = WhaleWalletCopier(etherscan_api_key="YourAPIKey")

# Sample wallets to screen (replace with real addresses)
wallets = [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "0x220866B1A2219f40e72f5c628B65D54268cA3A9D",
    #... add more wallets
]

# Run complete workflow: discover whales → monitor → report
copier.quick_start(
    sample_wallets=wallets,
    monitor_duration=60  # Monitor for 60 minutes
)
```

### Step-by-Step Usage

#### 1. Discover High-Performing Whales

```python
from scripts.whale_alerter import WhaleWalletCopier

copier = WhaleWalletCopier()

# Screen wallets for performance
whales = copier.discover_whales_from_list(
    wallet_addresses=["0x...", "0x...", ...],
    min_apy=100,  # >100% APY required
    days_back=30,  # Analyze last 30 days
    min_portfolio_value=10000  # Min $10k portfolio
)

# Save discovered whales
copier.save_whales_to_file("my_whales.json")

# Results
for whale in whales[:5]:
    print(f"Wallet: {whale['wallet']}")
    print(f"APY: {whale['apy']:.1f}%")
    print(f"Value: ${whale['current_value_usd']:,.0f}")
```

#### 2. Monitor Whales for New Purchases

```python
# Monitor top 10 whales
signals = copier.start_monitoring(
    whale_wallets=[w['wallet'] for w in whales[:10]],
    check_interval=60,  # Check every 60 seconds
    duration_minutes=120,  # Monitor for 2 hours
    save_signals=True
)

# Real-time alerts will print to console:
# 🐋 WHALE PURCHASE DETECTED!
# Token: PEPE (Pepe)
# Price: $0.00000123
# Liquidity: $1,250,000
# Safety: 75/100 (MODERATE)
```

#### 3. Analyze Performance Manually

```python
from scripts.whale_performance_tracker import WhalePerformanceTracker

tracker = WhalePerformanceTracker()

result = tracker.calculate_wallet_performance(
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    days_back=30,
    min_value_usd=1000
)

if result['success']:
    perf = result['performance']
    print(f"APY: {perf['apy_percent']:.2f}%")
    print(f"Profit: ${perf['total_profit_usd']:,.2f}")
    print(f"ROI: {perf['roi_percent']:.2f}%")
    print(f"Is Whale: {perf['is_whale']}")
```

#### 4. Monitor Specific Wallet Transactions

```python
from scripts.transaction_monitor import TransactionMonitor

monitor = TransactionMonitor()

# Get recent transactions
txs = monitor.get_recent_transactions(
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    minutes_back=30
)

# Detect purchases
purchases = monitor.detect_new_purchases(
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    transactions=txs
)

# Analyze each purchase
for purchase in purchases:
    analysis = monitor.get_token_analysis(purchase['token_address'])
    print(f"Token: {purchase['token_symbol']}")
    print(f"Safety: {analysis['safety_score']}/100")
    print(f"Liquidity: ${analysis['liquidity_usd']:,.0f}")
```

---

## Configuration

### API Keys

```python
# Option 1: Environment variable
export ETHERSCAN_API_KEY="your_key"

# Option 2: Pass directly
copier = WhaleWalletCopier(etherscan_api_key="your_key")

# Option 3: Use free tier (limited to 5 calls/sec)
copier = WhaleWalletCopier()  # Uses default "YourApiKeyToken"
```

### Performance Thresholds

```python
# Adjust whale criteria
whales = copier.discover_whales_from_list(
    wallet_addresses=wallets,
    min_apy=150,  # More strict: >150% APY
    days_back=60,  # Longer period: 60 days
    min_portfolio_value=50000  # Higher minimum: $50k
)
```

### Monitoring Settings

```python
# Adjust monitoring parameters
signals = copier.start_monitoring(
    check_interval=30,  # Check more frequently (30s)
    duration_minutes=1440,  # Monitor for 24 hours
    save_signals=True
)
```

---

## How It Works

### 1. Performance Calculation

The system calculates wallet APY using this methodology:

#### Step 1: Fetch Transaction History
- Uses Etherscan API to get all ERC20 token transfers
- Filters by time window (e.g., last 30 days)

#### Step 2: Build Token Positions
- Tracks incoming transactions (buys)
- Tracks outgoing transactions (sells)
- Calculates net balance for each token

#### Step 3: Calculate Cost Basis
- Sums up all purchase amounts
- Approximates average entry price
- *Note: For production, fetch historical prices for exact cost basis*

#### Step 4: Get Current Value
- Fetches live token prices from DexScreener
- Multiplies balance × current price
- Sums across all positions

#### Step 5: Compute APY
```python
profit = current_value - cost_basis
roi = (profit / cost_basis) * 100
apy = (roi / days) * 365
```

### 2. Transaction Monitoring

The monitoring system works continuously:

#### Real-Time Polling
```
Every check_interval seconds:
  1. Fetch recent transactions for each whale wallet
  2. Filter for incoming token transfers (purchases)
  3. Exclude: sells, stablecoins, spam, self-transfers
  4. For each new purchase:
     a. Get token price & liquidity (DexScreener)
     b. Calculate safety score
     c. Generate alert with full analysis
```

#### Smart Filtering
- **Stablecoin Filter:** Ignores USDT, USDC, DAI (not interesting)
- **Spam Filter:** Removes transfers <0.01 tokens
- **Duplicate Detection:** Tracks last seen transaction per wallet
- **Safety Scoring:** 0-100 score based on liquidity, volume, market cap

### 3. Token Safety Analysis

Each token is scored on 4 dimensions (0-100 points):

| Metric | Weight | Criteria |
|--------|--------|----------|
| **Liquidity** | 40% | >$1M = 40pts, >$500k = 35pts, >$100k = 25pts |
| **Volume (24h)** | 25% | >$1M = 25pts, >$500k = 20pts, >$100k = 15pts |
| **Market Cap** | 20% | >$10M = 20pts, >$5M = 15pts, >$1M = 10pts |
| **Price Stability** | 15% | <10% change = 15pts, <25% = 10pts, <50% = 5pts |

**Safety Ratings:**
- 80-100: SAFE ✅
- 60-79: MODERATE ⚠️
- 40-59: RISKY ⚠️⚠️
- 0-39: HIGH RISK ❌

---

## Output Examples

### Whale Discovery Output

```
================================================================================
WHALE DISCOVERY PHASE
================================================================================
Screening: 50 wallets
Criteria:  APY >100%, Portfolio >$10,000
Period:    Last 30 days
================================================================================

[1/50] Analyzing 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb...
   ✅ WHALE IDENTIFIED!
      APY: 287.3%
      Value: $125,430
      Profit: $98,200

[2/50] Analyzing 0x220866B1A2219f40e72f5c628B65D54268cA3A9D...
   ⏭️ Does not meet criteria (APY: 45.2%, Value: $8,500)

...

================================================================================
✅ WHALE DISCOVERY COMPLETE
================================================================================
Found: 8 qualifying whales

Top 5 Performers:
1. 0x742d35Cc6634C053... - APY: 287.3%
2. 0x8f5e9Bf82Db3e... - APY: 195.7%
3. 0x3a2f1e84Cc5b9... - APY: 142.8%
4. 0x9d7c2Aa34Eb5f... - APY: 128.4%
5. 0x5b8e3Ff92Dc7a... - APY: 115.9%
================================================================================
```

### Purchase Alert Output

```
======================================================================
🐋 WHALE PURCHASE DETECTED!
======================================================================
Time:      2026-02-19 14:35:22
Wallet:    0x742d35Cc6634C053...
Token:     PEPE (PepeCoin)
Amount:    1,000,000,000 PEPE
Tx:        https://etherscan.io/tx/0xabc123...

📊 TOKEN ANALYSIS:
   Price:     $0.00000156
   Liquidity: $2,450,000
   24h Vol:   $850,000
   Market Cap: $15,600,000
   24h Change: +12.5%
   Safety:    82/100 (SAFE)
   Chart:     https://dexscreener.com/ethereum/0xdef456...
======================================================================

🎯 SIGNAL: BUY OPPORTUNITY
   Whale with 287% APY just bought PEPE
   High safety score (82/100)
   Strong liquidity ($2.45M)
   Consider buying: $0.00000156
```

### Performance Report Example

```
================================================================================
WALLET PERFORMANCE ANALYSIS
================================================================================
Wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
Period: 30 days

💰 FINANCIAL METRICS:
  Cost Basis:    $42,150.00
  Current Value: $125,430.00
  Profit:        $83,280.00
  ROI:           197.65%
  APY:           2,404.85%

🐋 WHALE STATUS: YES ✅

📈 TOP POSITIONS:
  PEPE: $45,200.00 (+315.2%)
  SHIB: $32,100.00 (+245.8%)
  WOJAK: $28,500.00 (+180.4%)
  DOGE: $19,630.00 (+52.3%)
  FLOKI: $0.00 (-100.0% - SOLD)
```

---

## API Integration

### Etherscan API

**Endpoint:** `https://api.etherscan.io/api`  
**Action:** `account > tokentx` (Get ERC20 token transfers)  
**Rate Limit:** 5 calls/sec (free tier), 50 calls/sec (paid)  
**Documentation:** https://docs.etherscan.io/api-endpoints/accounts

**Example Request:**
```python
params = {
    "module": "account",
    "action": "tokentx",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "startblock": 0,
    "endblock": 99999999,
    "sort": "desc",
    "apikey": "YOUR_API_KEY"
}
```

### DexScreener API

**Endpoint:** `https://api.dexscreener.com/latest/dex/tokens/{address}`  
**Rate Limit:** 300 calls/min (free, no API key needed)  
**Documentation:** https://docs.dexscreener.com/api/reference

**Example Response:**
```json
{
  "pairs": [{
    "priceUsd": "0.00000156",
    "liquidity": {"usd": 2450000},
    "volume": {"h24": 850000},
    "priceChange": {"h24": 12.5},
    "marketCap": 15600000
  }]
}
```

---

## Performance & Limitations

### Processing Times

| Operation | Duration | Notes |
|-----------|----------|-------|
| Wallet Performance Analysis | 3-5 seconds | Per wallet |
| Transaction Monitoring Check | 2-4 seconds | All whales combined |
| Token Safety Analysis | 1-2 seconds | Per token |
| Screen 100 Wallets | ~8 minutes | With rate limiting |

### Rate Limits

**Etherscan Free Tier:**
- 5 calls/second
- 100,000 calls/day
- Recommendation: Add 0.3s delay between requests

**DexScreener:**
- 300 calls/minute
- No daily limit
- No API key required

### Known Limitations

1. **Cost Basis Approximation**
   - Current: Uses simplified average purchase price
   - Limitation: Not exact unless you fetch historical prices
   - Production Fix: Integrate CoinGecko/CoinMarketCap historical API

2. **Chain Support**
   - Currently: Ethereum mainnet only (fully tested)
   - Possible: BSC, Polygon, Arbitrum (via similar APIs)
   - Requires: Chain-specific Etherscan-like API endpoints

3. **Real-Time Latency**
   - Typical Delay: 30-120 seconds behind actual trade
   - Reason: API polling interval + blockchain confirmation
   - Mitigation: Use WebSocket for true real-time (advanced)

4. **Spam/Scam Tokens**
   - Current: Basic filtering (stablecoins, small amounts)
   - Advanced: Add honeypot detection, contract verification
   - Recommendation: Always DYOR before buying

---

## Advanced Features

### Custom Whale Criteria

```python
# Find aggressive day traders (high frequency, short timeframes)
whales = tracker.identify_whale_wallets(
    wallet_addresses=wallets,
    min_apy=200,  # Very high APY
    days_back=7  # Short timeframe = active trader
)

# Find stable long-term investors
whales = tracker.identify_whale_wallets(
    wallet_addresses=wallets,
    min_apy=50,  # Lower but consistent
    days_back=90  # Longer timeframe
)
```

### Multi-Chain Support (Extended)

```python
# Monitor BSC whales
from scripts.whale_performance_tracker import WhalePerformanceTracker

tracker = WhalePerformanceTracker()
tracker.etherscan_api = "https://api.bscscan.com/api"  # BSC endpoint
tracker.etherscan_api_key = "YOUR_BSC_API_KEY"

result = tracker.calculate_wallet_performance(
    wallet_address="0x...",  # BSC wallet
    days_back=30
)
```

### Save & Load Whale Database

```python
# Save discovered whales
copier.save_whales_to_file("top_whales.json")

# Load later for monitoring
copier.load_whales_from_file("top_whales.json")

# Resume monitoring
signals = copier.start_monitoring(duration_minutes=120)
```

---

## Production Deployment

### Recommended Setup

```bash
# 1. Use dedicated server (VPS recommended)
# 2. Install dependencies
pip install requests

# 3. Set API key
export ETHERSCAN_API_KEY="your_production_key"

# 4. Run as background service
nohup python scripts/whale_alerter.py &

# 5. Set up alerts (Discord, Telegram, Email)
# See integration examples below
```

### Discord Integration (Example)

```python
import requests

def send_discord_alert(signal):
    webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK"
    
    embed = {
        "title": f"🐋 Whale Bought {signal['token_symbol']}!",
        "description": f"Safety: {signal['analysis']['safety_score']}/100",
        "color": 5814783,
        "fields": [
            {"name": "Price", "value": f"${signal['analysis']['price_usd']:.8f}"},
            {"name": "Liquidity", "value": f"${signal['analysis']['liquidity_usd']:,.0f}"},
            {"name": "Wallet", "value": signal['wallet'][:20] + "..."}
        ]
    }
    
    requests.post(webhook_url, json={"embeds": [embed]})

# Use in monitoring
signals = copier.start_monitoring(...)
for signal in signals:
    send_discord_alert(signal)
```

---

## Troubleshooting

### Common Issues

**Issue:** "No transactions found or API error"  
**Solution:** Check your Etherscan API key, verify wallet address format

**Issue:** "Rate limit exceeded"  
**Solution:** Add longer delays (`time.sleep(0.5)`) or upgrade to paid API tier

**Issue:** "No whales found"  
**Solution:** Lower `min_apy` threshold, increase `days_back`, or use different wallet list

**Issue:** "Token price not found"  
**Solution:** Token may not have liquidity on DEXs tracked by DexScreener

---

## Contributing

Found a bug or have a feature request? Contributions welcome!

---

## License

MIT License - Free to use and modify

---

## Disclaimer

**IMPORTANT:** This tool is for informational and educational purposes only.

- ⚠️ **Not Financial Advice:** Do not blindly copy whale trades
- ⚠️ **DYOR:** Always research tokens before buying
- ⚠️ **Risk:** Crypto trading is highly risky, you can lose money
- ⚠️ **Scams:** Not all tokens are legitimate, use safety scores as guidance
- ⚠️ **Regulations:** Ensure compliance with your local laws

Past performance (>100% APY) does not guarantee future results.

---

## Support

For questions, issues, or feedback:
- GitHub Issues: [Submit an issue]
- Community: Join the discussion
- Documentation: See README.md for more examples

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
