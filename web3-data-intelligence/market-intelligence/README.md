# Crypto Market Intelligence Skill

A comprehensive cryptocurrency market data and analysis skill for SpoonOS agents. Provides real-time price data, global market overview, token comparison, and trending analysis using the CoinGecko API.

## Overview

This skill fills the **market data intelligence gap** in the Web3 Data Intelligence track. While existing skills cover on-chain analysis (Etherscan) and security analysis (GoPlus/Tenderly), this skill provides the **market-facing data layer** that traders and analysts need for informed decision-making.

### Key Features

- **Token Price Analysis** - Real-time prices with 24h/7d/30d changes, ATH/ATL tracking, supply metrics
- **Global Market Overview** - Total market cap, BTC/ETH dominance, top coins, market mood analysis
- **Token Comparison** - Side-by-side comparison of up to 10 tokens across all key metrics
- **Trending Analysis** - Trending tokens by search popularity, top gainers and losers

### Data Source

All data is sourced from the [CoinGecko API](https://www.coingecko.com/en/api) (free tier). No API key required for basic endpoints.

## Quick Start

### For Vibe Coding (Claude Code / SpoonOS Skills)

```bash
# Copy to your skills directory
cp -r market-intelligence/ .claude/skills/market-intelligence/

# Or for agent workspace
cp -r market-intelligence/ .agent/skills/market-intelligence/
```

### For SpoonReactSkill Agent

```python
from spoon_ai.agents import SpoonReactSkill

agent = SpoonReactSkill(
    name="market_analyst",
    skill_paths=["path/to/web3-data-intelligence/market-intelligence"],
    scripts_enabled=True
)
await agent.activate_skill("crypto-market-intelligence")
result = await agent.run("What's the current price of Bitcoin?")
```

### Direct Script Execution

```bash
# Get Bitcoin price
echo '{"token_id": "bitcoin"}' | python3 scripts/token_price.py

# Get market overview
echo '{"limit": 10}' | python3 scripts/market_overview.py

# Compare tokens
echo '{"token_ids": ["bitcoin", "ethereum", "solana"]}' | python3 scripts/token_compare.py

# Get trending tokens
echo '{"type": "all"}' | python3 scripts/trending_tokens.py
```

## Scripts

| Script | Purpose | Input |
|--------|---------|-------|
| [token_price.py](scripts/token_price.py) | Real-time token price with full market data | `token_id`, `vs_currency` |
| [market_overview.py](scripts/market_overview.py) | Global market stats and top coins | `vs_currency`, `limit`, `category` |
| [token_compare.py](scripts/token_compare.py) | Side-by-side token comparison | `token_ids[]`, `vs_currency` |
| [trending_tokens.py](scripts/trending_tokens.py) | Trending tokens, gainers, losers | `type`, `vs_currency`, `limit` |

## Detailed API Documentation

### token_price.py

Fetches detailed price data for a single token or simple prices for multiple tokens.

**Single Token (Detailed):**

```json
// Input
{"token_id": "ethereum", "vs_currency": "usd"}

// Output
{
  "success": true,
  "token": {
    "id": "ethereum",
    "name": "Ethereum",
    "symbol": "ETH",
    "market_cap_rank": 2
  },
  "price": {
    "current": 3245.67,
    "currency": "USD",
    "market_cap": 390000000000,
    "total_volume_24h": 15000000000,
    "volume_mcap_ratio": 3.85
  },
  "changes": {
    "24h": 2.45,
    "7d": -1.23,
    "30d": 12.67
  },
  "ath": {
    "price": 4878.26,
    "date": "2021-11-10",
    "change_percentage": -33.47
  },
  "atl": {
    "price": 0.432979,
    "date": "2015-10-20",
    "change_percentage": 749567.12
  },
  "supply": {
    "circulating": 120000000,
    "total": 120000000,
    "max": null,
    "utilization": null
  }
}
```

**Multiple Tokens (Lightweight):**

```json
// Input
{"token_ids": ["bitcoin", "ethereum"], "vs_currency": "usd"}

// Output
{
  "success": true,
  "currency": "USD",
  "prices": {
    "bitcoin": {
      "price": 95432.10,
      "market_cap": 1890000000000,
      "volume_24h": 35000000000,
      "change_24h": 1.23
    },
    "ethereum": {
      "price": 3245.67,
      "market_cap": 390000000000,
      "volume_24h": 15000000000,
      "change_24h": 2.45
    }
  }
}
```

### market_overview.py

Fetches global market statistics and top coins ranked by market cap.

```json
// Input
{"vs_currency": "usd", "limit": 5, "category": "all"}

// Output
{
  "success": true,
  "currency": "USD",
  "global": {
    "total_market_cap_usd": 3200000000000,
    "total_volume_24h_usd": 120000000000,
    "market_cap_change_24h": 1.56,
    "btc_dominance": 52.3,
    "eth_dominance": 16.8,
    "active_cryptocurrencies": 14523,
    "markets": 1100
  },
  "top_coins": [...],
  "insights": {
    "market_mood": "Slightly Bullish",
    "avg_change_24h": 1.42,
    "gainers_count": 4,
    "losers_count": 1,
    "best_performer": "Solana",
    "worst_performer": "XRP"
  }
}
```

### token_compare.py

Compares 2-10 tokens side by side with automated insights.

```json
// Input
{"token_ids": ["bitcoin", "ethereum", "solana"], "vs_currency": "usd"}

// Output
{
  "success": true,
  "tokens_compared": 3,
  "tokens": [
    {
      "name": "Bitcoin",
      "symbol": "BTC",
      "rank": 1,
      "price": 95432.10,
      "market_cap": 1890000000000,
      "volume_24h": 35000000000,
      "volume_mcap_ratio": 1.85,
      "changes": {"24h": 1.23, "7d": 5.67, "30d": 15.89},
      "ath": {"price": 108786, "change": -12.27},
      "supply": {"circulating": 19800000, "total": 19800000, "max": 21000000}
    },
    ...
  ],
  "insights": {
    "best_24h_performer": {"name": "Solana", "change": 4.56},
    "worst_24h_performer": {"name": "Bitcoin", "change": 1.23},
    "best_7d_performer": {"name": "Ethereum", "change": 8.90},
    "highest_volume_activity": {"name": "Bitcoin", "ratio": 1.85},
    "closest_to_ath": {"name": "Bitcoin", "distance": -12.27}
  }
}
```

### trending_tokens.py

Fetches trending tokens and computes top gainers/losers from top 250 coins.

```json
// Input
{"type": "all", "vs_currency": "usd", "limit": 5}

// Output
{
  "success": true,
  "currency": "USD",
  "trending": [
    {"rank": 1, "name": "Pepe", "symbol": "PEPE", "market_cap_rank": 23},
    ...
  ],
  "top_gainers": [
    {"name": "TokenX", "symbol": "TKX", "change_24h": 45.67, "price": 1.23},
    ...
  ],
  "top_losers": [
    {"name": "TokenY", "symbol": "TKY", "change_24h": -23.45, "price": 0.56},
    ...
  ],
  "insights": {
    "hottest_token": {"name": "Pepe", "symbol": "PEPE"},
    "biggest_gainer": {"name": "TokenX", "change": 45.67},
    "biggest_loser": {"name": "TokenY", "change": -23.45}
  }
}
```

**Query types:**
- `"all"` - Returns trending + gainers + losers (default)
- `"trending"` - Only trending tokens by search popularity
- `"gainers"` - Only top gainers
- `"losers"` - Only top losers

## Configuration

### Supported Currencies

Prices can be returned in any of these currencies:

| Fiat | Crypto |
|------|--------|
| USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR | BTC, ETH, BNB, SOL, XRP |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COINGECKO_API_KEY` | No | Optional Pro API key for higher rate limits |

**No API key is required for basic usage.** The free CoinGecko API supports 10-30 calls/minute.

## Error Handling

All scripts return structured error responses:

```json
{"error": "Rate limit exceeded. Please wait before retrying."}
{"error": "Token not found: invalid-token-id"}
{"error": "Unsupported currency: xyz. Supported: usd, eur, gbp, ..."}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Rate limit exceeded | Too many requests | Wait 1-2 minutes before retrying |
| Token not found | Invalid CoinGecko ID | Use CoinGecko search to find correct ID |
| Unsupported currency | Invalid currency code | Use one of the supported currencies |
| Connection error | Network issues | Check internet connectivity |

## Security

- **No API keys required** for basic functionality (CoinGecko free tier)
- **No private keys** are ever needed - this is a read-only data skill
- **Input validation** on all parameters (token IDs, currencies, limits)
- **Safe error messages** - no stack traces or internal details exposed
- **No hardcoded secrets** - optional API key loaded from environment only
- **Rate limit awareness** - clear error messages when limits are hit

## Use Cases

1. **Portfolio Monitoring** - Track prices of tokens you hold
2. **Market Analysis** - Assess overall market conditions before trading
3. **Token Research** - Compare competing tokens before investing
4. **Trend Spotting** - Identify trending tokens and momentum shifts
5. **Price Alerts** - Monitor token prices against target levels
6. **Reporting** - Generate market overview reports for teams

## Example Agent Interactions

```
User: "What's Bitcoin trading at right now?"
Agent: Activates token_price tool -> Returns BTC price with changes

User: "Give me a crypto market overview"
Agent: Activates market_overview tool -> Returns global stats + top coins

User: "Compare ETH, SOL, and AVAX"
Agent: Activates token_compare tool -> Returns side-by-side comparison

User: "What's trending in crypto today?"
Agent: Activates trending_tokens tool -> Returns trending + gainers/losers
```

## Composability

This skill is designed to compose well with other Web3 Data Intelligence skills:

- **+ On-Chain Analysis**: Get price data, then dive into on-chain metrics
- **+ Security Analysis**: Check trending tokens for security risks
- **+ DeFi Skills**: Compare token prices before swapping on DEXes
- **+ Bridge Skills**: Compare prices across chains before bridging

## License

MIT License
