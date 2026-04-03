# Rug Pull Probability Scorer

> **Production-ready token safety analysis system** that combines on-chain data, security APIs, and liquidity metrics to generate comprehensive 0-100 safety scores for ERC-20 tokens.

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## 🎯 Overview

The Rug Pull Probability Scorer is a sophisticated cryptocurrency token analysis tool that helps investors identify potential scams, rug pulls, and high-risk tokens before investing. It performs multi-dimensional analysis across four key areas:

| Category | Weight | Analysis Focus |
|----------|--------|----------------|
| **Contract Security** | 30% | Honeypot detection, malicious functions, ownership, verification |
| **Holder Distribution** | 25% | Centralization risk, whale concentration, holder count |
| **Liquidity Status** | 35% | Pool depth, liquidity locks, multi-DEX presence |
| **Trading Analysis** | 10% | Buy/sell taxes, transferability, restrictions |

**Risk Levels**:
- 🟢 **Very Low (86-100)**: Safe to trade with high confidence
- 🟢 **Low (71-85)**: Generally safe, suitable for trading
- 🟡 **Moderate (51-70)**: Proceed with caution, small amounts only
- 🔴 **High (31-50)**: Not recommended, high chance of losses
- 🔴 **Critical (0-30)**: DO NOT INVEST, likely scam

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd web3-data-intelligence/rugpull-probability-scorer

# Install dependencies
pip install web3 requests

# Optional: Set up environment variables for premium features
cp .env.example .env  # Edit with your API keys
```

### Basic Usage

```python
from scripts.safety_scorer import SafetyScorer

# Initialize the scorer
scorer = SafetyScorer()

# Analyze a token
result = scorer.analyze_token(
    token_address="0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
    chain="ethereum",
    detailed=True
)

# Display results
print(f"Safety Score: {result['safety_score']}/100")
print(f"Risk Level: {result['risk_level']}")
print(f"Recommendation: {result['recommendation']}")
```

### Quick Test

```bash
# Run the production test suite
python test_analyzer.py

# Tests 3 major tokens (DAI, USDC, WETH)
# Expected completion time: ~10 seconds
```

---

## 📊 Features

### Core Analysis Modules

#### 1. Contract Security Analyzer
```python
from scripts.contract_analyzer import ContractAnalyzer

analyzer =ContractAnalyzer()
result = analyzer.analyze_contract(
    token_address="0x...",
    chain="ethereum"
)

# Returns:
# - Security score (0-30 points)
# - Honeypot detection status
# - Malicious function identification
# - Ownership status
# - Contract verification
```

**Detection Capabilities**:
- ✅ Honeypot contracts (via Honeypot.is API)
- ✅ Mint functions (unlimited token creation)
- ✅ Blacklist mechanisms
- ✅ Pausable transfers
- ✅ Ownership control
- ✅ Hidden fees
- ✅ Proxy patterns

#### 2. Holder Distribution Analyzer
```python
from scripts.holder_analyzer import HolderAnalyzer

analyzer = HolderAnalyzer()
result = analyzer.analyze_holders(
    token_address="0x...",
    chain="ethereum"
)

# Returns:
# - Holder distribution score (0-25 points)
# - Top holder concentration
# - Centralization risk level
# - CEX wallet filtering
# - Holder count estimation
```

**Analysis Metrics**:
- Top holder percentage
- Top 10 holders concentration
- Non-CEX holder distribution
- Gini coefficient (inequality measure)
- Centralization warnings

#### 3. Liquidity Analyzer
```python
from scripts.liquidity_analyzer import LiquidityAnalyzer

analyzer = LiquidityAnalyzer()
result = analyzer.analyze_liquidity(
    token_address="0x...",
    chain="ethereum"
)

# Returns:
# - Liquidity score (0-35 points)
# - Total liquidity across all pools
# - Lock status and duration
# - Multi-DEX distribution
# - Liquidity warnings
```

**Monitored Aspects**:
- Total USD liquidity across DEXs
- Liquidity lock detection (Unicrypt, Team.Finance, PinkSale)
- Lock duration and amount
- Number of liquidity pools
- DEX distribution (Uniswap, Sushiswap, etc.)

#### 4. Comprehensive Safety Scorer
```python
from scripts.safety_scorer import SafetyScorer

scorer = SafetyScorer()
result = scorer.analyze_token(
    token_address="0x...",
    chain="ethereum",
    detailed=True  # Include full breakdown
)

# Returns complete analysis with:
# - Overall safety score (0-100)
# - Risk level determination
# - Confidence percentage
# - Detailed score breakdown
# - Investment recommendation
# - Warnings and red flags
```

---

## 🔌 API Integration

The scorer integrates with multiple real-world APIs for comprehensive analysis:

### 1. GoPlus Security API
**Endpoint**: `https://api.gopluslabs.io/api/v1`
- Token security scanning
- Malicious pattern detection
- Contract risk assessment
- **Status**: ✅ Public, no API key required

### 2. Honeypot.is API
**Endpoint**: `https://api.honeypot.is/v2`
- Trading simulation
- Buy/sell tax detection
- Honeypot identification
- **Status**: ✅ Public, no API key required

### 3. DexScreener API
**Endpoint**: `https://api.dexscreener.com/latest`
- Liquidity pool discovery
- DEX price and volume data
- Multi-chain support
- **Status**: ✅ Public, no API key required

### 4. Blockchain RPC
**Endpoint**: Configurable (default: LlamaRPC)
- On-chain Transfer event scanning
- Token supply queries
- Smart contract interactions
- **Status**: ⚠️ Free tier has rate limits

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file for optional premium features:

```bash
# Optional: For enhanced holder analysis
# Free tier available from all providers
ALCHEMY_API_KEY=your_alchemy_key
INFURA_API_KEY=your_infura_key
QUICKNODE_API_KEY=your_quicknode_key

# Optional: For contract verification checks
ETHERSCAN_API_KEY=your_etherscan_key
BSCSCAN_API_KEY=your_bscscan_key
POLYGONSCAN_API_KEY=your_polygonscan_key
```

### Supported Chains

| Chain | Status | RPC Endpoint | Notes |
|-------|--------|--------------|-------|
| Ethereum | ✅ Full | `https://eth.llamarpc.com` | Mainnet supported |
| BSC | ✅ Full | `https://bsc-dataseed.binance.org` | Binance Smart Chain |
| Polygon | ✅ Full | `https://polygon-rpc.com` | Matic mainnet |
| Arbitrum | ✅ Full | `https://arb1.arbitrum.io/rpc` | Layer 2 |
| Base | ✅ Full | `https://mainnet.base.org` | Coinbase L2 |

To add custom RPC endpoints:

```python
# In holder_analyzer.py or liquidity_analyzer.py
RPC_URLS = {
    "ethereum": "https://your-premium-rpc-endpoint.com",
    # ... other chains
}
```

---

## 📈 Usage Examples

### Example 1: Quick Safety Check

```python
from scripts.safety_scorer import SafetyScorer

scorer = SafetyScorer()

# Analyze unknown token
result = scorer.analyze_token(
    token_address="0x...",
    chain="ethereum"
)

if result['risk_level'] in ['Very Low', 'Low']:
    print(f"✅ Safe to trade (Score: {result['safety_score']}/100)")
else:
    print(f"⚠️ High risk! {', '.join(result['red_flags'])}")
```

### Example 2: Detailed Analysis Report

```python
result = scorer.analyze_token(
    token_address="0x...",
    chain="ethereum",
    detailed=True
)

print(f"\n{'='*60}")
print(f"Token Analysis Report")
print(f"{'='*60}")
print(f"Safety Score: {result['safety_score']}/100")
print(f"Risk Level: {result['risk_level']}")
print(f"Confidence: {result['confidence']}%\n")

print("Score Breakdown:")
print(f"  Contract Security: {result['breakdown']['contract_score']}/30")
print(f"  Holder Distribution: {result['breakdown']['holder_score']}/25")
print(f"  Liquidity Status: {result['breakdown']['liquidity_score']}/35")
print(f"  Trading Analysis: {result['breakdown']['trading_score']}/10\n")

if result['warnings']:
    print(f"⚠️  Warnings ({len(result['warnings'])}):")
    for warning in result['warnings']:
        print(f"   • {warning}")

if result['red_flags']:
    print(f"\n🚩 Red Flags ({len(result['red_flags'])}):")
    for flag in result['red_flags']:
        print(f"   • {flag}")

print(f"\n💡 Recommendation: {result['recommendation']}")
```

### Example 3: Batch Analysis

```python
tokens = [
    ("0x6B175474E89094C44Da98b954EedeAC495271d0F", "DAI"),
    ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDC"),
    ("0xdAC17F958D2ee523a2206206994597C13D831ec7", "USDT"),
]

scorer = SafetyScorer()
results = []

for address, name in tokens:
    result = scorer.analyze_token(address, "ethereum")
    results.append({
        "name": name,
        "score": result['safety_score'],
        "risk": result['risk_level']
    })
    print(f"{name}: {result['safety_score']}/100 ({result['risk_level']})")

# Sort by safety score
results.sort(key=lambda x: x['score'], reverse=True)
print(f"\nSafest token: {results[0]['name']}")
```

### Example 4: Contract-Only Analysis

```python
from scripts.contract_analyzer import ContractAnalyzer

analyzer = ContractAnalyzer()
result = analyzer.analyze_contract(
    token_address="0x...",
    chain="ethereum"
)

if result['is_honeypot']:
    print("🚨 WARNING: Honeypot detected!")
elif result['malicious_functions']:
    print(f"⚠️ Malicious functions found: {', '.join(result['malicious_functions'])}")
else:
    print("✅ Contract appears safe")
```

---

## 🏗️ Architecture

```
rugpull-probability-scorer/
├── scripts/
│   ├── contract_analyzer.py      # Contract security analysis
│   ├── holder_analyzer.py         # Token holder distribution analysis
│   ├── liquidity_analyzer.py      # Liquidity pool analysis
│   └── safety_scorer.py           #Main orchestrator & scoring logic
├── SKILL.md                       # Comprehensive skill documentation
├── PULL.md                        # Production test results
├── README.md                      # This file
└── test_analyzer.py               # Automated test suite
```

### Data Flow

```
Token Address → SafetyScorer
                     ↓
        ┌───────────┴───────────┐
        ↓           ↓            ↓
ContractAnalyzer  HolderAnalyzer  LiquidityAnalyzer
        ↓           ↓            ↓
    GoPlus API   On-chain RPC    DexScreener API
    Honeypot.is  Transfer Events  Pool Data
        ↓           ↓            ↓
    Score 0-30   Score 0-25    Score 0-35
        └───────────┬───────────┘
                    ↓
            Trading Analysis (0-10)
                    ↓
        Final Score (0-100) + Risk Level
```

---

## ⚙️ Scoring Methodology

### Contract Security (30 points)

| Factor | Points | Criteria |
|--------|--------|----------|
| Not a honeypot | 10 | Honeypot.is simulation passes |
| Verified contract | 5 | Source code verified on block explorer |
| No mint function | 5 | Cannot create unlimited tokens |
| Ownership renounced | 3 | Owner cannot change contract |
| No blacklist | 3 | Cannot freeze individual wallets |
| Not a proxy | 2 | Implementation cannot be changed |
| No hidden fees | 2 | Transparent fee structure |

**Penalties**:
- Honeypot detected: -10 points (critical)
- Mint function: -5 points
- Active ownership with control: -3 points
- Blacklist capability: -3 points

### Holder Distribution (25 points)

| Factor | Points | Calculation |
|--------|--------|-------------|
| Low concentration | 0-15 | Based on top 10 holder % |
| Sufficient holders | 0-10 | Based on unique holder count |

**Scoring Logic**:
- Top 10 < 30%: +15 points (excellent distribution)
- Top 10 30-50%: +10 points (good distribution)
- Top 10 50-70%: +5 points (concerning concentration)
- Top 10 > 70%: 0 points (extreme centralization)

- Holders > 1000: +10 points
- Holders 200-1000: +7 points
- Holders 50-200: +3 points
- Holders < 50: 0 points

### Liquidity Analysis (35 points)

| Factor | Points | Criteria |
|--------|--------|----------|
| Liquidity locked | 15 | Tokens locked in trusted contracts |
| Sufficient liquidity | 10 | Minimum thresholds met |
| Multiple pools | 5 | Distributed across DEXs |
| Lock duration | 5 | Longer locks score higher |

**Liquidity Thresholds**:
- ≥ $100k: Safe (10 points)
- ≥ $50k: Moderate (7 points)
- ≥ $10k: Low (3 points)
- < $10k: Very risky (0 points)

### Trading Analysis (10 points)

| Factor | Points | Criteria |
|--------|--------|----------|
| Can sell | 5 | Transfer function works |
| Low taxes | 5 | Buy/sell taxes < 10% |

---

## 🔍 Interpreting Results

### Understanding Safety Scores

**86-100 Points (Very Low Risk)**:
- Well-established token with excellent metrics
- High liquidity, distributed holders
- Clean contract with no major red flags
- Safe for most investors

**71-85 Points (Low Risk)**:
- Generally safe with minor concerns
- Good liquidity and distribution
- May have some technical warnings but not critical
- Suitable for most trading strategies

**51-70 Points (Moderate Risk)**:
- Proceed with caution
- Some concerning indicators present
- Limited liquidity or concentrated holders
- Research thoroughly before investing
- Consider small position sizes only

**31-50 Points (High Risk)**:
- Not recommended for investment
- Multiple red flags present
- High chance of loss
- Consider avoiding entirely

**0-30 Points (Critical Risk)**:
- DO NOT INVEST
- Likely scam or rug pull
- Extreme red flags (honeypot, severe centralization, etc.)
- High probability of total loss

### Common Warnings Explained

| Warning | Meaning | Severity |
|---------|---------|----------|
| "Contract not verified" | Source code not published | Moderate |
| "Can mint unlimited tokens" |  Token supply can be increased | Moderate-High |
| "Proxy contract" | Implementation can be upgraded | Low-Moderate |
| "Top holder owns X%" | Centralization risk | Varies |
| "Liquidity not locked" | Can beremoved anytime | High |
| "Honeypot detected" | Cannot sell after buying | Critical |
| "Blacklist function" | Wallets can be frozen | High |

---

## 🚨 Limitations & Disclaimers

### Known Limitations

1. **Holder Data Accuracy**:
   - Free RPC endpoints have strict rate limits
   - Holder analysis based on recent on-chain activity (last 1,000 blocks)
   - Individual balance queries disabled on free tier
   - **Solution**: Use paid RPC providers for complete holder data

2. **Contract Verification**:
   - Some verified contracts may show as unverified due to API data lag
   - Complex upgrade patterns (like MakerDAO) may cause verification issues
   - **Solution**: Cross-reference with Etherscan manually for critical decisions

3. **Analysis Speed**:
   - Average analysis time: 2-3 seconds per token
   - May be slower during high network congestion
   - RPC rate limits can cause intermittent delays

4. **Reputation Scoring**:
   - Technical analysis only - does not account for project reputation
   - Major tokens (DAI, USDC, WETH) may score lower due to complex contracts
   - **Recommendation**: Combine with reputation/whitelist systems

### Important Disclaimers

⚠️ **NOT FINANCIAL ADVICE**: This tool provides technical analysis only. Always conduct your own research.

⚠️ **NO GUARANTEES**: A high safety score does not guarantee profit or prevent loss. Markets are unpredictable.

⚠️ **KNOWN-GOOD TOKENS MAY SCORE LOW**: Established tokens with complex contracts (stablecoins, governance tokens) may have lower scores due to technical patterns that trigger warnings.

⚠️ **EVOLVING THREATS**: New scam techniques emerge constantly. This tool covers known patterns but cannot detect novel attacks.

⚠️ **API DEPENDENCY**: Analysis quality depends on third-party API availability and accuracy.

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: "RPC connection failed"
```
Solution: The free RPC endpoint is temporarily unavailable. 
Options:
1. Retry in a few seconds
2. Set custom RPC in environment variables
3. Use paid RPC provider (Alchemy, Infura, QuickNode)
```

**Issue**: "No holder data available"
```
Solution: Rate limits exceeded or RPC connection issues.
Options:
1. Analysis continues with estimated holder metrics
2. Configure paid RPC endpoint for accurate data
3. Results remain valid - holder score is estimated conservatively
```

**Issue**: "Contract not verified - cannot audit code"
```
This is a warning, not an error. The analysis continues.
Note: Some verified contracts may show this due to API data lag.
Cross-check on Etherscan if critical.
```

**Issue**: Analysis takes > 10 seconds
```
Causes:
- Network congestion
- RPC rate limiting
- API timeouts

Solutions:
- Use premium RPC endpoints
- Implement caching layer
- Reduce concurrent requests
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

scorer = SafetyScorer()
result = scorer.analyze_token(...)
```

---

## 🚀 Production Deployment

### Recommended Enhancements

1. **Implement Caching**:
```python
import redis
from functools import lru_cache

# Cache API responses for 5 minutes
@lru_cache(maxsize=1000)
def cached_analysis(token_address, chain):
    return scorer.analyze_token(token_address, chain)
```

2. **Add Rate Limiting**:
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)  # 10 requests per minute
def analyze_with_limit(address, chain):
    return scorer.analyze_token(address, chain)
```

3. **Implement Token Whitelist**:
```python
KNOWN_SAFE_TOKENS = {
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": "WETH",
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": "DAI",
    # ... more tokens
}

def analyze_with_whitelist(address, chain):
    if address.lower() in KNOWN_SAFE_TOKENS:
        # Skip analysis or adjust scoring
        return enhanced_result
    return scorer.analyze_token(address, chain)
```

4. **Add Monitoring**:
```python
import sentry_sdk

sentry_sdk.init(dsn="your-sentry-dsn")

try:
    result = scorer.analyze_token(address, chain)
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

### Scalability Considerations

- **Horizontal Scaling**: Stateless design allows easy horizontal scaling
- **Database Integration**: Store historical analyses for trend tracking
- **Queue System**: Use Celery/RQ for background processing
- **Load Balancing**: Distribute requests across multiple instances
- **CDN Caching**: Cache common token analyses

---

## 📚 Additional Resources

- **SKILL.md**: Complete technical documentation and API reference
- **PULL.md**: Production test results and validation
- **test_analyzer.py**: Comprehensive test suite with real examples

### Related Projects

- [GoPlus Security](https://gopluslabs.io/): Token security database
- [Honeypot.is](https://honeypot.is/): Honeypot detection service
- [DexScreener](https://dexscreener.com/): DEX liquidity aggregator

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional chain support
- More security pattern detection
- Enhanced holder analysis algorithms
- Performance optimizations
- Additional API integrations

---

## ⚡ Performance

- **Analysis Speed**: < 3 seconds per token
- **API Success Rate**: >99.5% (based on production tests)
- **Accuracy**: Technical analysis only - cannot predict future events
- **Concurrent Requests**: Supports parallel analysis (with rate limiting)

---

**Status**: ✅ Production Ready (v1.0)  
**Last Updated**: February 19, 2026  
**Maintainer**: XSpoonAi  
**Repository**: github.com/XSpoonAi/spoon-awesome-skill

---

## Quick Links

- 📖 [Full Documentation](SKILL.md)
- ✅ [Test Results](PULL.md)
- 🐛 [Report Issues](https://github.com/XSpoonAi/spoon-awesome-skill/issues)
- 💬 [Community Support](https://github.com/XSpoonAi/spoon-awesome-skill/discussions)
