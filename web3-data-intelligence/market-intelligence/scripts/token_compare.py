#!/usr/bin/env python3
"""
Token Compare Script
Compares multiple cryptocurrencies side by side using CoinGecko API.

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error

COINGECKO_API = "https://api.coingecko.com/api/v3"

SUPPORTED_CURRENCIES = [
    "usd", "eur", "gbp", "jpy", "aud", "cad", "chf", "cny", "inr",
    "btc", "eth", "bnb", "sol", "xrp"
]

# Maximum tokens to compare at once
MAX_COMPARE = 10


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


def validate_token_id(token_id: str) -> str:
    """Validate and sanitize token ID input."""
    sanitized = token_id.lower().strip()
    if not sanitized:
        raise ValueError("Token ID cannot be empty")
    if len(sanitized) > 100:
        raise ValueError("Token ID too long")
    if not all(c.isalnum() or c in "-." for c in sanitized):
        raise ValueError(f"Token ID contains invalid characters: {sanitized}")
    return sanitized


def validate_currency(vs_currency: str) -> str:
    """Validate and normalize currency input."""
    currency = vs_currency.lower().strip()
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(
            f"Unsupported currency: {currency}. "
            f"Supported: {', '.join(SUPPORTED_CURRENCIES[:10])}"
        )
    return currency


def compare_tokens(token_ids: list[str], vs_currency: str = "usd") -> dict:
    """Compare multiple tokens across key metrics."""
    if not token_ids:
        raise ValueError("Provide at least 2 token IDs to compare")
    if len(token_ids) < 2:
        raise ValueError("Need at least 2 tokens for comparison")
    if len(token_ids) > MAX_COMPARE:
        raise ValueError(f"Maximum {MAX_COMPARE} tokens can be compared at once")

    validated_ids = [validate_token_id(tid) for tid in token_ids]
    vs_currency = validate_currency(vs_currency)

    ids_str = ",".join(validated_ids)
    url = (
        f"{COINGECKO_API}/coins/markets"
        f"?vs_currency={vs_currency}"
        f"&ids={ids_str}"
        f"&order=market_cap_desc"
        f"&sparkline=false"
        f"&price_change_percentage=24h,7d,30d"
    )

    data = fetch_json(url)

    if not isinstance(data, list):
        raise ValueError("Unexpected response format from API")

    if not data:
        raise ValueError(
            f"No tokens found. Check IDs: {', '.join(validated_ids)}"
        )

    # Build comparison data
    tokens = []
    for coin in data:
        market_cap = coin.get("market_cap", 0) or 0
        volume = coin.get("total_volume", 0) or 0

        tokens.append({
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "rank": coin.get("market_cap_rank"),
            "price": coin.get("current_price", 0),
            "market_cap": market_cap,
            "volume_24h": volume,
            "volume_mcap_ratio": round(
                (volume / market_cap * 100), 2
            ) if market_cap > 0 else 0,
            "changes": {
                "24h": round(
                    coin.get("price_change_percentage_24h", 0) or 0, 2
                ),
                "7d": round(
                    coin.get("price_change_percentage_7d_in_currency", 0) or 0, 2
                ),
                "30d": round(
                    coin.get("price_change_percentage_30d_in_currency", 0) or 0, 2
                )
            },
            "ath": {
                "price": coin.get("ath", 0),
                "change": round(
                    coin.get("ath_change_percentage", 0) or 0, 2
                )
            },
            "supply": {
                "circulating": coin.get("circulating_supply"),
                "total": coin.get("total_supply"),
                "max": coin.get("max_supply")
            }
        })

    # Generate comparison insights
    best_24h = max(tokens, key=lambda x: x["changes"]["24h"])
    worst_24h = min(tokens, key=lambda x: x["changes"]["24h"])
    best_7d = max(tokens, key=lambda x: x["changes"]["7d"])
    highest_vol_ratio = max(tokens, key=lambda x: x["volume_mcap_ratio"])
    closest_ath = max(tokens, key=lambda x: x["ath"]["change"])

    # Check which tokens were not found
    found_ids = {t["id"] for t in tokens}
    missing = [tid for tid in validated_ids if tid not in found_ids]

    return {
        "success": True,
        "currency": vs_currency.upper(),
        "tokens_compared": len(tokens),
        "tokens": tokens,
        "insights": {
            "best_24h_performer": {
                "name": best_24h["name"],
                "change": best_24h["changes"]["24h"]
            },
            "worst_24h_performer": {
                "name": worst_24h["name"],
                "change": worst_24h["changes"]["24h"]
            },
            "best_7d_performer": {
                "name": best_7d["name"],
                "change": best_7d["changes"]["7d"]
            },
            "highest_volume_activity": {
                "name": highest_vol_ratio["name"],
                "ratio": highest_vol_ratio["volume_mcap_ratio"]
            },
            "closest_to_ath": {
                "name": closest_ath["name"],
                "distance": closest_ath["ath"]["change"]
            }
        },
        "missing_tokens": missing if missing else None
    }


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        token_ids = input_data.get("token_ids", [])
        vs_currency = input_data.get("vs_currency", "usd")

        if not token_ids:
            print(json.dumps({
                "error": "Provide 'token_ids' as a list of CoinGecko token IDs",
                "example": {"token_ids": ["bitcoin", "ethereum", "solana"]}
            }))
            sys.exit(1)

        result = compare_tokens(token_ids, vs_currency)
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
