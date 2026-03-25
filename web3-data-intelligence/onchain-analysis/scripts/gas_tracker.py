#!/usr/bin/env python3
"""
Gas Tracker Script
Fetches current gas prices and provides recommendations
"""

import json
import sys
import os
import urllib.request
import urllib.error
from typing import Optional

# Chain configurations
CHAIN_CONFIG = {
    "ethereum": {
        "api_url": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "native_symbol": "ETH",
        "block_time": 12
    },
    "polygon": {
        "api_url": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
        "native_symbol": "POL",  # Renamed from MATIC on Sept 4, 2024
        "block_time": 2
    },
    "arbitrum": {
        "api_url": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
        "native_symbol": "ETH",
        "block_time": 0.25
    },
    "optimism": {
        "api_url": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_API_KEY",
        "native_symbol": "ETH",
        "block_time": 2
    },
    "base": {
        "api_url": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
        "native_symbol": "ETH",
        "block_time": 2
    }
}

# Common transaction gas limits
GAS_LIMITS = {
    "eth_transfer": 21000,
    "erc20_transfer": 65000,
    "erc20_approve": 46000,
    "nft_transfer": 85000,
    "nft_mint": 200000,
    "uniswap_swap": 150000,
    "uniswap_add_liquidity": 250000,
    "aave_deposit": 200000,
    "aave_borrow": 300000,
    "contract_deploy": 500000
}


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    """Fetch data from Etherscan-like API"""
    if api_key:
        params["apikey"] = api_key

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GasTracker/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def get_gas_price(chain: str) -> dict:
    """Get current gas prices from Etherscan"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "gastracker",
        "action": "gasoracle"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        result = data.get("result", {})
        return {
            "low": float(result.get("SafeGasPrice", 0)),
            "standard": float(result.get("ProposeGasPrice", 0)),
            "fast": float(result.get("FastGasPrice", 0)),
            "base_fee": float(result.get("suggestBaseFee", 0)) if result.get("suggestBaseFee") else None
        }

    # Fallback: get gas price from eth_gasPrice
    params = {
        "module": "proxy",
        "action": "eth_gasPrice"
    }

    data = fetch_api(config["api_url"], params, api_key)
    if data.get("result"):
        gas_price_wei = int(data["result"], 16)
        gas_price_gwei = gas_price_wei / 1e9
        return {
            "low": gas_price_gwei * 0.8,
            "standard": gas_price_gwei,
            "fast": gas_price_gwei * 1.2,
            "base_fee": None
        }

    raise ValueError("Could not fetch gas prices")


def get_eth_price() -> float:
    """Get current ETH price in USD"""
    try:
        params = {
            "module": "stats",
            "action": "ethprice"
        }
        api_key = os.getenv("ETHERSCAN_API_KEY")
        data = fetch_api("https://api.etherscan.io/api", params, api_key)

        if data.get("status") == "1":
            return float(data["result"].get("ethusd", 0))
    except:
        pass

    return 0  # Unable to fetch price


def calculate_tx_cost(gas_limit: int, gas_price_gwei: float, eth_price: float) -> dict:
    """Calculate transaction cost in ETH and USD"""
    gas_price_wei = gas_price_gwei * 1e9
    cost_wei = gas_limit * gas_price_wei
    cost_eth = cost_wei / 1e18
    cost_usd = cost_eth * eth_price if eth_price > 0 else 0

    return {
        "gas_limit": gas_limit,
        "gas_price_gwei": gas_price_gwei,
        "cost_eth": round(cost_eth, 6),
        "cost_usd": round(cost_usd, 2)
    }


def get_gas_analysis(chain: str, priority: str = "standard") -> dict:
    """Get comprehensive gas analysis"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    # Get gas prices
    gas_prices = get_gas_price(chain)

    # Get ETH price for USD calculations
    eth_price = get_eth_price() if chain in ["ethereum", "arbitrum", "optimism", "base"] else 0

    # Calculate costs for common operations
    priority_map = {
        "low": "low",
        "standard": "standard",
        "medium": "standard",
        "fast": "fast",
        "high": "fast"
    }
    selected_priority = priority_map.get(priority, "standard")
    selected_gas_price = gas_prices.get(selected_priority, gas_prices["standard"])

    operation_costs = {}
    for op_name, gas_limit in GAS_LIMITS.items():
        operation_costs[op_name] = calculate_tx_cost(gas_limit, selected_gas_price, eth_price)

    # Estimate confirmation times (simplified)
    block_time = config["block_time"]
    confirmation_times = {
        "low": f"~{int(block_time * 10)} seconds" if block_time < 5 else f"~{int(block_time * 10 / 60)} minutes",
        "standard": f"~{int(block_time * 3)} seconds" if block_time < 20 else f"~{int(block_time * 3 / 60)} minutes",
        "fast": f"~{int(block_time)} seconds"
    }

    # Gas level assessment
    if chain == "ethereum":
        if gas_prices["standard"] > 50:
            gas_level = "HIGH"
            recommendation = "Gas prices are elevated. Consider waiting for lower prices if not urgent."
        elif gas_prices["standard"] > 20:
            gas_level = "MEDIUM"
            recommendation = "Gas prices are moderate. Good time for non-urgent transactions."
        else:
            gas_level = "LOW"
            recommendation = "Gas prices are low. Good time to execute transactions."
    else:
        # L2s typically have much lower gas
        gas_level = "LOW" if gas_prices["standard"] < 1 else "MEDIUM"
        recommendation = f"L2 gas prices on {chain.title()} are typically very low."

    return {
        "success": True,
        "chain": chain,
        "native_symbol": config["native_symbol"],
        "eth_price_usd": eth_price,
        "gas_prices_gwei": {
            "low": round(gas_prices["low"], 2),
            "standard": round(gas_prices["standard"], 2),
            "fast": round(gas_prices["fast"], 2),
            "base_fee": round(gas_prices["base_fee"], 2) if gas_prices["base_fee"] else None
        },
        "confirmation_times": confirmation_times,
        "selected_priority": selected_priority,
        "operation_costs": operation_costs,
        "analysis": {
            "gas_level": gas_level,
            "recommendation": recommendation,
            "best_time_hint": "Weekends and early UTC morning typically have lower gas"
        }
    }


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        chain = input_data.get("chain", "ethereum")
        priority = input_data.get("priority", "standard")

        result = get_gas_analysis(chain, priority)
        print(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
