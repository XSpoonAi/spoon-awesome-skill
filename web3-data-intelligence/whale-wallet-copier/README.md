# 🐋 Whale Wallet Copier - Trading Intelligence Skill

> Identify wallets that made >100% APY in the last month and get alerted when they buy new tokens

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-success.svg)]()

##

 What This Does

Transform raw on-chain data into actionable trading intelligence by:

1. **📊 Analyzing** wallet performance to calculate APY from transaction history
2. **🔍 Discovering** high-performing whales (>100% APY in 30 days)
3. **⚡ Monitoring** whale wallets in real-time for new token purchases
4. **🎯 Alerting** you instantly with complete token analysis (price, liquidity, safety)
5. **💡 Signaling** actionable buy opportunities backed by proven performers

**Why This Matters:** Know what successful traders are buying *before* the crowd does.

---

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to skill directory
cd web3-data-intelligence/whale-wallet-copier

# Install dependencies
pip install requests

# Optional: Set API key for higher rate limits
export ETHERSCAN_API_KEY="your_etherscan_api_key"
```

### 2. Run Example

```python
from scripts.whale_alerter import WhaleWalletCopier

# Initialize
copier = WhaleWalletCopier()

# Sample wallets to screen (replace with real addresses)
wallets = [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "0x220866B1A2219f40e72f5c628B65D54268cA3A9D",
    # ... add more wallets
]

# Discover whales → Monitor purchases → Generate alerts
copier.quick_start(
    sample_wallets=wallets,
    monitor_duration=60  # Monitor for 60 minutes
)
```

### 3. See Results

```
🐋 WHALE PURCHASE DETECTED!
======================================================================
Time:      2026-02-19 14:35:22
Wallet:    0x742d35Cc6634C053...
Token:     PEPE (PepeCoin)
Amount:    1,000,000,000 PEPE

📊 TOKEN ANALYSIS:
   Price:     $0.00000156
   Liquidity: $2,450,000
   Safety:    82/100 (SAFE)
   Chart:     https://dexscreener.com/ethereum/0xdef456...
======================================================================
```

---

## 📖 Usage Examples

### Example 1: Discover Whale Wallets

Find wallets with >100% APY in the last 30 days:

```python
from scripts.whale_alerter import WhaleWalletCopier

copier = WhaleWalletCopier(etherscan_api_key="your_key")

# Screen 100 wallets
wallet_list = ["0x...", "0x...", ...]  # Your list of addresses

whales = copier.discover_whales_from_list(
    wallet_addresses=wallet_list,
    min_apy=100,  # Minimum 100% APY
    days_back=30,  # Last 30 days
    min_portfolio_value=10000  # Min $10k portfolio
)

# Print results
for whale in whales:
    print(f"Wallet: {whale['wallet']}")
    print(f"APY: {whale['apy']:.1f}%")
    print(f"Portfolio: ${whale['current_value_usd']:,.0f}")
    print(f"Profit: ${whale['profit_usd']:,.0f}\n")

# Save for later
copier.save_whales_to_file("my_whales.json")
```

**Output:**
```
Wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
APY: 287.3%
Portfolio: $125,430
Profit: $98,200

Wallet: 0x8f5e9Bf82Db3e8Ca9d4B7F5e3A2c1D8b0E6f4A9c
APY: 195.7%
Portfolio: $78,900
Profit: $52,100
```

### Example 2: Monitor Whale Purchases

Track specific whales for new token buys:

```python
# Load previously discovered whales
copier.load_whales_from_file("my_whales.json")

# Monitor top 10 whales
signals = copier.start_monitoring(
    whale_wallets=[w['wallet'] for w in copier.known_whales[:10]],
    check_interval=60,  # Check every 60 seconds
    duration_minutes=120,  # Monitor for 2 hours
    save_signals=True  # Save to JSON file
)

# Signals are automatically printed in real-time
# JSON file saved as: whale_signals_20260219_143022.json
```

### Example 3: Analyze Single Wallet

Deep dive into one wallet's performance:

```python
from scripts.whale_performance_tracker import WhalePerformanceTracker

tracker = WhalePerformanceTracker(etherscan_api_key="your_key")

result = tracker.calculate_wallet_performance(
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    days_back=30,
    min_value_usd=1000  # Only positions >$1000
)

if result['success']:
    perf = result['performance']
    
    print(f"💰 FINANCIAL METRICS")
    print(f"Cost Basis:    ${perf['total_cost_basis_usd']:,.2f}")
    print(f"Current Value: ${perf['total_current_value_usd']:,.2f}")
    print(f"Profit:        ${perf['total_profit_usd']:,.2f}")
    print(f"ROI:           {perf['roi_percent']:.2f}%")
    print(f"APY:           {perf['apy_percent']:.2f}%")
    print(f"Is Whale:      {perf['is_whale']}")
    
    print(f"\n📈 TOP POSITIONS:")
    for pos in result['positions'][:5]:
        print(f"  {pos['token']}: ${pos['current_value_usd']:,.0f} "
              f"({pos['roi_percent']:+.1f}%)")
```

### Example 4: Custom Monitoring Script

Create a custom monitoring loop:

```python
from scripts.transaction_monitor import TransactionMonitor
import time

monitor = TransactionMonitor(etherscan_api_key="your_key")

whale_wallets = [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "0x8f5e9Bf82Db3e8Ca9d4B7F5e3A2c1D8b0E6f4A9c"
]

print("🔍 Starting custom monitoring...")

while True:
    for wallet in whale_wallets:
        # Get recent transactions (last 5 minutes)
        txs = monitor.get_recent_transactions(wallet, minutes_back=5)
        
        # Detect new purchases
        purchases = monitor.detect_new_purchases(wallet, txs)
        
        for purchase in purchases:
            # Get token analysis
            analysis = monitor.get_token_analysis(purchase['token_address'])
            
            if analysis and analysis['safety_score'] >= 60:
                print(f"\n🎯 BUY SIGNAL!")
                print(f"Whale: {wallet[:20]}...")
                print(f"Token: {purchase['token_symbol']}")
                print(f"Price: ${analysis['price_usd']:.8f}")
                print(f"Safety: {analysis['safety_score']}/100")
                print(f"Liquidity: ${analysis['liquidity_usd']:,.0f}")
    
    time.sleep(60)  # Check every minute
```

### Example 5: Token Safety Analysis

Analyze any token before buying:

```python
from scripts.transaction_monitor import TransactionMonitor

monitor = TransactionMonitor()

# Analyze a specific token
token_address = "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"  # SHIB

analysis = monitor.get_token_analysis(token_address)

if analysis:
    print(f"Token Analysis for {token_address}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Price:       ${analysis['price_usd']:.10f}")
    print(f"Liquidity:   ${analysis['liquidity_usd']:,.0f}")
    print(f"24h Volume:  ${analysis['volume_24h']:,.0f}")
    print(f"Market Cap:  ${analysis['market_cap']:,.0f}")
    print(f"24h Change:  {analysis['price_change']['24h']:+.2f}%")
    print(f"Safety:      {analysis['safety_score']}/100 ({analysis['safety_rating']})")
    print(f"DEX:         {analysis['dex']}")
    print(f"Chart:       {analysis['url']}")
else:
    print("❌ Token not found or no liquidity")
```

---

## 🔧 Configuration

### API Keys

```bash
# Etherscan API Key (optional, recommended for production)
# Free tier: 5 calls/sec, 100k calls/day
# Get one at: https://etherscan.io/apis
export ETHERSCAN_API_KEY="your_key_here"

# DexScreener (no API key needed)
# Free tier: 300 calls/min
```

### Adjusting Whale Criteria

```python
# Strict criteria (fewer, higher quality whales)
whales = copier.discover_whales_from_list(
    wallet_addresses=wallets,
    min_apy=200,  # Very high APY
    days_back=30,
    min_portfolio_value=50000  # $50k minimum
)

# Relaxed criteria (more whales, lower threshold)
whales = copier.discover_whales_from_list(
    wallet_addresses=wallets,
    min_apy=50,  # Lower APY
    days_back=60,  # Longer period
    min_portfolio_value=5000  # $5k minimum
)
```

### Monitoring Frequency

```python
# High frequency (real-time, resource intensive)
signals = copier.start_monitoring(
    check_interval=30,  # Every 30 seconds
    duration_minutes=60
)

# Low frequency (less resource intensive)
signals = copier.start_monitoring(
    check_interval=300,  # Every 5 minutes
    duration_minutes=1440  # 24 hours
)
```

---

## 📊 Performance Benchmarks

| Operation | Time | API Calls |
|-----------|------|-----------|
| Analyze 1 wallet | ~3-5s | 2-3 calls |
| Screen 100 wallets | ~8 mins | 200-300 calls |
| Monitor 10 whales (1 check) | ~4s | 10-20 calls |
| Token analysis | ~1-2s | 1 call |

**Estimated API Usage:**
- Discover 100 wallets: ~300 Etherscan calls, ~100 DexScreener calls
- Monitor 10 whales for 24h (60s interval): ~14,400 Etherscan calls

**Rate Limits:**
- Etherscan Free: 5 calls/sec → Max 100 wallets every ~10 minutes
- DexScreener: 300 calls/min → No practical limit for this use case

---

## 🎯 Real-World Use Cases

### Use Case 1: Copy Trading Bot

Build an automated copy trading system:

```python
# 1. Discover top performers weekly
whales = copier.discover_whales_from_list(wallets, min_apy=150)
copier.save_whales_to_file("top_whales.json")

# 2. Monitor 24/7
while True:
    signals = copier.start_monitoring(duration_minutes=60)
    
    # 3. Execute trades automatically
    for signal in signals:
        if signal['analysis']['safety_score'] >= 70:
            execute_trade(signal)  # Your trading logic here
```

### Use Case 2: Research Dashboard

Track whale activity for research:

```python
import pandas as pd

# Collect signals over 7 days
all_signals = []

for day in range(7):
    signals = copier.start_monitoring(duration_minutes=1440)
    all_signals.extend(signals)

# Convert to DataFrame
df = pd.DataFrame([{
    'token': s['token_symbol'],
    'price': s['analysis']['price_usd'],
    'safety': s['analysis']['safety_score'],
    'whale_count': s['wallet']
} for s in all_signals])

# Analyze trends
top_tokens = df.groupby('token').size().sort_values(ascending=False)
print("Most bought tokens by whales:", top_tokens.head(10))
```

### Use Case 3: Alert System

Set up notifications to your phone/Discord:

```python
import requests

def send_telegram_alert(signal):
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    
    message = f"""
🐋 WHALE PURCHASE DETECTED!

Token: {signal['token_symbol']}
Price: ${signal['analysis']['price_usd']:.8f}
Safety: {signal['analysis']['safety_score']}/100
Liquidity: ${signal['analysis']['liquidity_usd']:,.0f}

Chart: {signal['analysis']['url']}
    """
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

# Use in monitoring
signals = copier.start_monitoring(duration_minutes=120)
for signal in signals:
    if signal['analysis']['safety_score'] >= 70:
        send_telegram_alert(signal)
```

---

## 🛠️ Troubleshooting

### Problem: "No transactions found or API error"

**Solution:**
- Check your Etherscan API key is correct
- Verify wallet address is valid (0x... format)
- Ensure wallet has ERC20 token transactions

```python
# Test API key
tracker = WhalePerformanceTracker(etherscan_api_key="test_key")
result = tracker.get_wallet_transactions("0x742d35Cc...")
print(len(result))  # Should return > 0
```

### Problem: "Rate limit exceeded"

**Solution:**
- Add delays between requests
- Upgrade to paid Etherscan tier
- Reduce number of wallets screened

```python
# Add delay
import time
for wallet in wallets:
    result = tracker.calculate_wallet_performance(wallet)
    time.sleep(1)  # 1 second delay
```

### Problem: "No whales found"

**Solution:**
- Lower `min_apy` threshold (try 50% instead of 100%)
- Increase `days_back` (try 60 days instead of 30)
- Use different wallet list (may need better data source)

```python
# Relaxed criteria
whales = copier.discover_whales_from_list(
    wallet_addresses=wallets,
    min_apy=50,  # Lower threshold
    days_back=60  # Longer period
)
```

### Problem: "Token price not found"

**Solution:**
- Token may not have active DEX trading
- Check if token is on Ethereum mainnet
- Verify token address is correct

```python
# Manual check
monitor = TransactionMonitor()
analysis = monitor.get_token_analysis("0x...")
if not analysis:
    print("Token not found on DexScreener")
```

---

## 📁 File Structure

```
whale-wallet-copier/
├── scripts/
│   ├── whale_performance_tracker.py   # Calculate wallet APY
│   ├── transaction_monitor.py          # Monitor transactions
│   └── whale_alerter.py                # Main orchestrator
├── SKILL.md                            # Complete documentation
├── README.md                           # This file
└── PULL.md                             # Contribution summary
```

---

## 🔐 Security & Privacy

**This tool is read-only:**
- ✅ Only reads on-chain data (public information)
- ✅ No private keys required
- ✅ No wallet connections needed
- ✅ Cannot execute trades (monitoring only)

**Privacy:**
- All wallet addresses are public on Ethereum blockchain
- This tool only accesses publicly available data
- No personal information is collected

---

## ⚠️ Disclaimer

**IMPORTANT - READ BEFORE USING:**

- 📢 **Not Financial Advice:** This tool is for educational and informational purposes only
- ⚠️ **High Risk:** Cryptocurrency trading is extremely risky. You can lose all your money
- 🔍 **DYOR:** Always do your own research before buying any token
- 🚫 **No Guarantees:** Past performance (>100% APY) does NOT guarantee future results
- 💀 **Scam Risk:** Many tokens are scams/rug pulls,even with high safety scores
- 📜 **Legal:** Ensure compliance with your local laws and regulations
- 🤝 **Responsibility:** You are solely responsible for your trading decisions

**The creators of this tool are not responsible for any financial losses.**

---

## 🤝 Contributing

Found a bug? Have a feature idea? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📜 License

MIT License - Free to use and modify

Copyright (c) 2026 Sambit (Community Contributor)

---

## 🆘 Support

**Need help?**
- 📖 See [SKILL.md](SKILL.md) for detailed documentation
- 💬 Join the community discussion
- 🐛 Report bugs via GitHub Issues

---

## 🌟 Acknowledgments

Built with:
- [Etherscan API](https://etherscan.io/apis) - Transaction data
- [DexScreener API](https://dexscreener.com) - Token prices & analytics
- Python requests library

---

**Happy Whale Watching! 🐋📈**

*Remember: Trade responsibly, always DYOR, and never invest more than you can afford to lose.*
