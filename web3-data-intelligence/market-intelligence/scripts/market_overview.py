#!/usr/bin/env python3
"""
Market Overview Script
Fetches global crypto market statistics and top coins from CoinGecko API.

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Optional

COINGECKO_API = "https://api.coingecko.com/api/v3"

SUPPORTED_CURRENCIES = [
    "usd", "eur", "gbp", "jpy", "aud", "cad", "chf", "cny", "inr",
    "btc", "eth", "bnb", "sol", "xrp"
]


def fetch_json(url: str) -> dict:
    """Fetch JSON data from URL with error handling."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "CryptoMarketIntelligence/1.0",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise ConnectionError("Rate limit exceeded. Please wait before retrying.")
        raise ConnectionError(f"HTTP error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def validate_currency(vs_currency: str) -> str:
    """Validate and normalize currency input."""
    currency = vs_currency.lower().strip()
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(
            f"Unsupported currency: {currency}. "
            f"Supported: {', '.join(SUPPORTED_CURRENCIES[:10])}"
        )
    return currency


def validate_limit(limit: int) -> int:
    """Validate results limit."""
    if not isinstance(limit, int) or limit < 1:
        return 10
    return min(limit, 100)


def get_global_stats() -> dict:
    """Get global cryptocurrency market statistics."""
    url = f"{COINGECKO_API}/global"
    data = fetch_json(url)

    if not data or "data" not in data:
        raise ValueError("Failed to fetch global market data")

    global_data = data["data"]
    market_cap = global_data.get("total_market_cap", {})
    volume = global_data.get("total_volume", {})
    dominance = global_data.get("market_cap_percentage", {})

    return {
        "total_market_cap_usd": round(market_cap.get("usd", 0), 2),
        "total_volume_24h_usd": round(volume.get("usd", 0), 2),
        "market_cap_change_24h": round(
            global_data.get("market_cap_change_percentage_24h_usd", 0), 2
        ),
        "btc_dominance": round(dominance.get("btc", 0), 2),
        "eth_dominance": round(dominance.get("eth", 0), 2),
        "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
        "markets": global_data.get("markets", 0),
        "updated_at": global_data.get("updated_at", 0)
    }


def get_top_coins(
    vs_currency: str = "usd",
    limit: int = 10,
    category: Optional[str] = None
) -> list[dict]:
    """Get top coins by market cap."""
    vs_currency = validate_currency(vs_currency)
    limit = validate_limit(limit)

    url = (
        f"{COINGECKO_API}/coins/markets"
        f"?vs_currency={vs_currency}"
        f"&order=market_cap_desc"
        f"&per_page={limit}"
        f"&page=1"
        f"&sparkline=false"
        f"&price_change_percentage=24h,7d,30d"
    )

    if category and category != "all":
        # Sanitize category input
        safe_category = "".join(
            c for c in category.lower().strip() if c.isalnum() or c == "-"
        )
        url += f"&category={safe_category}"

    data = fetch_json(url)

    if not isinstance(data, list):
        raise ValueError("Unexpected response format from API")

    coins = []
    for coin in data:
        coins.append({
            "rank": coin.get("market_cap_rank"),
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "price": coin.get("current_price", 0),
            "market_cap": coin.get("market_cap", 0),
            "volume_24h": coin.get("total_volume", 0),
            "change_24h": round(
                coin.get("price_change_percentage_24h", 0) or 0, 2
            ),
            "change_7d": round(
                coin.get("price_change_percentage_7d_in_currency", 0) or 0, 2
            ),
            "change_30d": round(
                coin.get("price_change_percentage_30d_in_currency", 0) or 0, 2
            ),
            "circulating_supply": coin.get("circulating_supply"),
            "total_supply": coin.get("total_supply"),
            "ath": coin.get("ath", 0),
            "ath_change": round(
                coin.get("ath_change_percentage", 0) or 0, 2
            )
        })

    return coins


def get_market_overview(
    vs_currency: str = "usd",
    limit: int = 10,
    category: Optional[str] = None
) -> dict:
    """Get comprehensive market overview."""
    global_stats = get_global_stats()
    top_coins = get_top_coins(vs_currency, limit, category)

    # Calculate sector insights from top coins
    total_volume = sum(c.get("volume_24h", 0) or 0 for c in top_coins)
    avg_change_24h = (
        sum(c.get("change_24h", 0) or 0 for c in top_coins) / len(top_coins)
        if top_coins else 0
    )

    gainers = [c for c in top_coins if (c.get("change_24h") or 0) > 0]
    losers = [c for c in top_coins if (c.get("change_24h") or 0) < 0]

    # Determine market mood
    if avg_change_24h > 3:
        mood = "Bullish"
    elif avg_change_24h > 0:
        mood = "Slightly Bullish"
    elif avg_change_24h > -3:
        mood = "Slightly Bearish"
    else:
        mood = "Bearish"

    return {
        "success": True,
        "currency": vs_currency.upper(),
        "global": global_stats,
        "top_coins": top_coins,
        "insights": {
            "market_mood": mood,
            "avg_change_24h": round(avg_change_24h, 2),
            "gainers_count": len(gainers),
            "losers_count": len(losers),
            "top_volume_24h": total_volume,
            "best_performer": max(
                top_coins, key=lambda x: x.get("change_24h") or 0
            ).get("name") if top_coins else None,
            "worst_performer": min(
                top_coins, key=lambda x: x.get("change_24h") or 0
            ).get("name") if top_coins else None
        }
    }


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        vs_currency = input_data.get("vs_currency", "usd")
        limit = input_data.get("limit", 10)
        category = input_data.get("category")

        result = get_market_overview(vs_currency, limit, category)
        print(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)
    except (ValueError, ConnectionError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {type(e).__name__}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
