#!/usr/bin/env python3
"""
Trending Tokens Script
Fetches trending tokens, top gainers, and losers from CoinGecko API.

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
    return min(limit, 50)


def get_trending() -> dict:
    """Get trending tokens by search popularity on CoinGecko."""
    url = f"{COINGECKO_API}/search/trending"
    data = fetch_json(url)

    if not data or "coins" not in data:
        raise ValueError("Failed to fetch trending data")

    trending = []
    for item in data.get("coins", []):
        coin = item.get("item", {})
        trending.append({
            "rank": coin.get("score", 0) + 1,
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "market_cap_rank": coin.get("market_cap_rank"),
            "price_btc": coin.get("price_btc", 0),
            "small_image": coin.get("small", "")
        })

    return trending


def get_top_gainers_losers(
    vs_currency: str = "usd",
    limit: int = 10
) -> dict:
    """Get top gainers and losers by 24h price change."""
    vs_currency = validate_currency(vs_currency)

    # Fetch top 250 coins to find gainers/losers
    url = (
        f"{COINGECKO_API}/coins/markets"
        f"?vs_currency={vs_currency}"
        f"&order=market_cap_desc"
        f"&per_page=250"
        f"&page=1"
        f"&sparkline=false"
        f"&price_change_percentage=24h,7d"
    )

    data = fetch_json(url)

    if not isinstance(data, list):
        raise ValueError("Unexpected response format from API")

    # Filter out coins with no price change data
    valid_coins = [
        c for c in data
        if c.get("price_change_percentage_24h") is not None
    ]

    # Sort for gainers (highest 24h change)
    sorted_by_gain = sorted(
        valid_coins,
        key=lambda x: x.get("price_change_percentage_24h", 0),
        reverse=True
    )

    # Sort for losers (lowest 24h change)
    sorted_by_loss = sorted(
        valid_coins,
        key=lambda x: x.get("price_change_percentage_24h", 0)
    )

    safe_limit = validate_limit(limit)

    def format_coin(coin: dict) -> dict:
        return {
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "rank": coin.get("market_cap_rank"),
            "price": coin.get("current_price", 0),
            "market_cap": coin.get("market_cap", 0),
            "volume_24h": coin.get("total_volume", 0),
            "change_24h": round(
                coin.get("price_change_percentage_24h", 0) or 0, 2
            ),
            "change_7d": round(
                coin.get("price_change_percentage_7d_in_currency", 0) or 0, 2
            )
        }

    gainers = [format_coin(c) for c in sorted_by_gain[:safe_limit]]
    losers = [format_coin(c) for c in sorted_by_loss[:safe_limit]]

    return {
        "gainers": gainers,
        "losers": losers
    }


def get_trending_analysis(
    vs_currency: str = "usd",
    limit: int = 10,
    query_type: Optional[str] = None
) -> dict:
    """Get comprehensive trending analysis."""
    result: dict = {
        "success": True,
        "currency": vs_currency.upper()
    }

    if query_type in (None, "trending", "all"):
        trending = get_trending()
        result["trending"] = trending
        result["trending_count"] = len(trending)

    if query_type in (None, "gainers", "losers", "all"):
        gl_data = get_top_gainers_losers(vs_currency, limit)
        result["top_gainers"] = gl_data["gainers"]
        result["top_losers"] = gl_data["losers"]

    # Generate insights
    insights = {}

    if "trending" in result and result["trending"]:
        top_trending = result["trending"][0]
        insights["hottest_token"] = {
            "name": top_trending["name"],
            "symbol": top_trending["symbol"]
        }

    if "top_gainers" in result and result["top_gainers"]:
        top_gainer = result["top_gainers"][0]
        insights["biggest_gainer"] = {
            "name": top_gainer["name"],
            "change": top_gainer["change_24h"]
        }

    if "top_losers" in result and result["top_losers"]:
        top_loser = result["top_losers"][0]
        insights["biggest_loser"] = {
            "name": top_loser["name"],
            "change": top_loser["change_24h"]
        }

    result["insights"] = insights

    return result


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        query_type = input_data.get("type", "all")
        vs_currency = input_data.get("vs_currency", "usd")
        limit = input_data.get("limit", 10)

        result = get_trending_analysis(vs_currency, limit, query_type)
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
