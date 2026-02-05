#!/usr/bin/env python3
"""
Token Price Script
Fetches real-time cryptocurrency price data from CoinGecko API.

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Optional

COINGECKO_API = "https://api.coingecko.com/api/v3"

# Supported fiat and crypto currencies
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


def validate_token_id(token_id: str) -> str:
    """Validate and sanitize token ID input."""
    sanitized = token_id.lower().strip()
    if not sanitized:
        raise ValueError("Token ID cannot be empty")
    if len(sanitized) > 100:
        raise ValueError("Token ID too long")
    # Only allow alphanumeric, hyphens, and dots
    if not all(c.isalnum() or c in "-." for c in sanitized):
        raise ValueError("Token ID contains invalid characters")
    return sanitized


def get_token_price(token_id: str, vs_currency: str = "usd") -> dict:
    """Get detailed price data for a specific token."""
    token_id = validate_token_id(token_id)
    vs_currency = validate_currency(vs_currency)

    url = (
        f"{COINGECKO_API}/coins/{token_id}"
        f"?localization=false&tickers=false&community_data=false"
        f"&developer_data=false&sparkline=false"
    )

    data = fetch_json(url)

    if not data or "id" not in data:
        raise ValueError(f"Token not found: {token_id}")

    market = data.get("market_data", {})
    cur = vs_currency

    # Extract price data
    current_price = market.get("current_price", {}).get(cur, 0)
    market_cap = market.get("market_cap", {}).get(cur, 0)
    total_volume = market.get("total_volume", {}).get(cur, 0)

    # Price changes
    price_change_24h = market.get("price_change_percentage_24h")
    price_change_7d = market.get("price_change_percentage_7d")
    price_change_30d = market.get("price_change_percentage_30d")

    # ATH / ATL
    ath = market.get("ath", {}).get(cur, 0)
    ath_date = market.get("ath_date", {}).get(cur, "N/A")
    ath_change = market.get("ath_change_percentage", {}).get(cur, 0)

    atl = market.get("atl", {}).get(cur, 0)
    atl_date = market.get("atl_date", {}).get(cur, "N/A")
    atl_change = market.get("atl_change_percentage", {}).get(cur, 0)

    # Supply data
    circulating = market.get("circulating_supply")
    total_supply = market.get("total_supply")
    max_supply = market.get("max_supply")

    # Volume to market cap ratio
    vol_mcap_ratio = (total_volume / market_cap * 100) if market_cap > 0 else 0

    return {
        "success": True,
        "token": {
            "id": data.get("id"),
            "name": data.get("name"),
            "symbol": data.get("symbol", "").upper(),
            "image": data.get("image", {}).get("small", ""),
            "market_cap_rank": data.get("market_cap_rank")
        },
        "price": {
            "current": current_price,
            "currency": cur.upper(),
            "market_cap": market_cap,
            "total_volume_24h": total_volume,
            "volume_mcap_ratio": round(vol_mcap_ratio, 2)
        },
        "changes": {
            "24h": round(price_change_24h, 2) if price_change_24h else None,
            "7d": round(price_change_7d, 2) if price_change_7d else None,
            "30d": round(price_change_30d, 2) if price_change_30d else None
        },
        "ath": {
            "price": ath,
            "date": ath_date[:10] if ath_date != "N/A" else "N/A",
            "change_percentage": round(ath_change, 2) if ath_change else None
        },
        "atl": {
            "price": atl,
            "date": atl_date[:10] if atl_date != "N/A" else "N/A",
            "change_percentage": round(atl_change, 2) if atl_change else None
        },
        "supply": {
            "circulating": circulating,
            "total": total_supply,
            "max": max_supply,
            "utilization": round(
                (circulating / max_supply * 100), 2
            ) if circulating and max_supply else None
        },
        "last_updated": market.get("last_updated", "N/A")
    }


def get_simple_price(token_ids: list[str], vs_currency: str = "usd") -> dict:
    """Get simple price data for multiple tokens (lightweight)."""
    validated_ids = [validate_token_id(tid) for tid in token_ids]
    vs_currency = validate_currency(vs_currency)

    ids_str = ",".join(validated_ids)
    url = (
        f"{COINGECKO_API}/simple/price"
        f"?ids={ids_str}"
        f"&vs_currencies={vs_currency}"
        f"&include_24hr_change=true"
        f"&include_market_cap=true"
        f"&include_24hr_vol=true"
    )

    data = fetch_json(url)

    results = {}
    for token_id in validated_ids:
        token_data = data.get(token_id, {})
        results[token_id] = {
            "price": token_data.get(vs_currency, 0),
            "market_cap": token_data.get(f"{vs_currency}_market_cap", 0),
            "volume_24h": token_data.get(f"{vs_currency}_24h_vol", 0),
            "change_24h": round(
                token_data.get(f"{vs_currency}_24h_change", 0), 2
            )
        }

    return {
        "success": True,
        "currency": vs_currency.upper(),
        "prices": results
    }


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        token_id = input_data.get("token_id", "")
        token_ids = input_data.get("token_ids", [])
        vs_currency = input_data.get("vs_currency", "usd")

        if token_ids:
            result = get_simple_price(token_ids, vs_currency)
        elif token_id:
            result = get_token_price(token_id, vs_currency)
        else:
            result = {"error": "Provide 'token_id' or 'token_ids' parameter"}

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
