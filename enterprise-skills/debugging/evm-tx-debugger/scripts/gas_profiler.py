#!/usr/bin/env python3
"""
EVM Gas Profiler
Profiles gas usage of a transaction, calculates efficiency metrics,
compares with network averages, and provides optimization recommendations.

Input (JSON via stdin):
{
    "tx_hash": "0x...",
    "chain": "ethereum"
}

Output (JSON via stdout):
{
    "success": true,
    "scan_type": "gas_profile",
    "transaction": { ... },
    "gas_metrics": { ... },
    "eip1559": { ... },
    "cost": { ... },
    "network_comparison": { ... },
    "efficiency_score": { ... }
}

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error
import time
import re
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BLOCKSCOUT_CHAINS: Dict[str, str] = {
    "ethereum": "https://eth.blockscout.com",
    "bsc": "https://bsc.blockscout.com",
    "polygon": "https://polygon.blockscout.com",
    "arbitrum": "https://arbitrum.blockscout.com",
    "base": "https://base.blockscout.com",
    "optimism": "https://optimism.blockscout.com",
    "avalanche": "https://avax.blockscout.com",
}

CHAIN_IDS: Dict[str, str] = {
    "ethereum": "1", "eth": "1",
    "bsc": "56", "bnb": "56",
    "polygon": "137", "matic": "137",
    "arbitrum": "42161", "arb": "42161",
    "base": "8453",
    "optimism": "10", "op": "10",
    "avalanche": "43114", "avax": "43114",
}

CHAIN_NATIVE_CURRENCY: Dict[str, str] = {
    "ethereum": "ETH",
    "bsc": "BNB",
    "polygon": "MATIC",
    "arbitrum": "ETH",
    "base": "ETH",
    "optimism": "ETH",
    "avalanche": "AVAX",
}

# Base gas cost for a simple ETH transfer
SIMPLE_TRANSFER_GAS: int = 21000

TX_HASH_PATTERN: re.Pattern = re.compile(r"^0x[a-fA-F0-9]{64}$")

MAX_RETRIES: int = 3
RETRY_BACKOFF: float = 1.0

# Gas usage thresholds for common operation types
OPERATION_GAS_RANGES: Dict[str, Tuple[int, int]] = {
    "simple_transfer": (21000, 21000),
    "erc20_transfer": (45000, 75000),
    "erc20_approve": (25000, 50000),
    "nft_transfer": (50000, 100000),
    "nft_mint": (80000, 250000),
    "dex_swap": (100000, 350000),
    "add_liquidity": (150000, 400000),
    "contract_deploy": (500000, 5000000),
    "complex_defi": (200000, 1000000),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_json(url: str, timeout: int = 15, retries: int = MAX_RETRIES) -> Optional[Dict]:
    """Fetch JSON from *url* with retry logic for 429 rate-limit responses."""
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "EVMTxDebugger/1.0",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                time.sleep(wait)
                last_err = exc
                continue
            if exc.code == 404:
                return None
            last_err = exc
            break
        except urllib.error.URLError as exc:
            last_err = exc
            break
    if last_err:
        raise ConnectionError(f"API request failed: {last_err}")
    return None


def _validate_tx_hash(tx_hash: str) -> str:
    """Validate and normalise a transaction hash."""
    tx_hash = tx_hash.strip()
    if not TX_HASH_PATTERN.match(tx_hash):
        raise ValueError(
            f"Invalid tx_hash format: {tx_hash}. "
            "Expected 0x followed by 64 hex characters."
        )
    return tx_hash.lower()


def _validate_chain(chain: str) -> str:
    """Validate chain name and return the canonical chain key."""
    chain_lower = chain.lower().strip()
    alias_to_canonical: Dict[str, str] = {
        "eth": "ethereum", "bnb": "bsc", "matic": "polygon",
        "arb": "arbitrum", "op": "optimism", "avax": "avalanche",
    }
    canonical = alias_to_canonical.get(chain_lower, chain_lower)
    if canonical not in BLOCKSCOUT_CHAINS:
        supported = ", ".join(sorted(BLOCKSCOUT_CHAINS.keys()))
        raise ValueError(f"Unsupported chain: {chain}. Supported chains: {supported}")
    return canonical


def _wei_to_eth(wei_val: int) -> float:
    """Convert wei to ETH as float."""
    return wei_val / 1e18


def _wei_to_gwei(wei_val: int) -> float:
    """Convert wei to Gwei as float."""
    return wei_val / 1e9


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------------------------
# Network stats
# ---------------------------------------------------------------------------

def _fetch_network_stats(chain: str) -> Optional[Dict[str, Any]]:
    """Fetch network-wide statistics from Blockscout."""
    base_url = BLOCKSCOUT_CHAINS[chain]
    url = f"{base_url}/api/v2/stats"
    try:
        data = _fetch_json(url, timeout=10, retries=2)
        if data and isinstance(data, dict):
            return data
    except ConnectionError:
        pass
    return None


def _extract_network_gas_info(stats: Optional[Dict]) -> Dict[str, Any]:
    """Extract gas-related info from network stats."""
    if not stats:
        return {
            "available": False,
            "avg_gas_price_gwei": None,
            "total_transactions": None,
        }

    gas_prices = stats.get("gas_prices", {})
    avg_price = None
    if isinstance(gas_prices, dict):
        # Blockscout returns gas_prices as {average, fast, slow}
        avg = gas_prices.get("average")
        if avg is not None:
            avg_price = float(avg)

    return {
        "available": True,
        "avg_gas_price_gwei": avg_price,
        "total_transactions": stats.get("total_transactions"),
        "network_utilization": stats.get("network_utilization_percentage"),
    }


# ---------------------------------------------------------------------------
# Gas analysis
# ---------------------------------------------------------------------------

def _identify_operation_type(tx_data: Dict) -> str:
    """Guess the operation type based on gas usage and transaction shape."""
    gas_used = _safe_int(tx_data.get("gas_used"))
    raw_input = tx_data.get("raw_input", tx_data.get("input", "0x"))
    to_info = tx_data.get("to")

    # Contract creation (no to address)
    if to_info is None or (isinstance(to_info, dict) and not to_info.get("hash")):
        return "contract_deploy"

    # Plain ETH transfer (no input data)
    if not raw_input or raw_input == "0x":
        return "simple_transfer"

    # Use gas ranges to guess
    if gas_used <= 21000:
        return "simple_transfer"
    elif gas_used <= 75000:
        return "erc20_transfer"
    elif gas_used <= 150000:
        return "nft_transfer"
    elif gas_used <= 350000:
        return "dex_swap"
    else:
        return "complex_defi"


def _compute_efficiency_score(gas_used: int, gas_limit: int) -> Dict[str, Any]:
    """Compute gas efficiency score (0-100).

    The score reflects how well-calibrated the gas limit was.
    100 = gas_used == gas_limit (perfect, but risky)
    Score penalises both over-allocation and near-exhaustion.

    Args:
        gas_used: Actual gas consumed.
        gas_limit: Gas limit set for the transaction.

    Returns:
        Dictionary with score, grade, and assessment.
    """
    if gas_limit <= 0 or gas_used <= 0:
        return {
            "score": 0,
            "grade": "N/A",
            "assessment": "Insufficient data to calculate efficiency.",
            "recommendations": [],
        }

    ratio = gas_used / gas_limit
    recommendations: List[str] = []

    # Ideal ratio is ~0.7-0.9 (some headroom but not wasteful)
    if ratio >= 0.99:
        # Exhausted -- very tight or out-of-gas
        score = 30
        grade = "D"
        assessment = "Gas limit was barely sufficient or exhausted. Transaction may have failed due to out-of-gas."
        recommendations.append("Increase gas limit by at least 25% to provide safety margin.")
    elif ratio >= 0.85:
        # Well calibrated
        score = 95
        grade = "A"
        assessment = "Excellent gas limit calibration. Usage is within optimal range."
    elif ratio >= 0.70:
        score = 90
        grade = "A"
        assessment = "Gas limit well-calibrated with reasonable safety margin."
    elif ratio >= 0.50:
        score = 65
        grade = "C"
        assessment = "Gas limit was generous. Consider reducing it closer to actual usage."
        ideal_limit = int(gas_used * 1.25)
        recommendations.append(f"Reduce gas limit to ~{ideal_limit:,} (1.25x actual usage).")
    elif ratio >= 0.30:
        score = 40
        grade = "D"
        assessment = "Significant gas over-allocation. Gas limit is much higher than needed."
        ideal_limit = int(gas_used * 1.25)
        recommendations.append(f"Reduce gas limit to ~{ideal_limit:,} (1.25x actual usage).")
        recommendations.append("Use eth_estimateGas for accurate limit estimation.")
    else:
        score = 20
        grade = "F"
        assessment = "Extreme gas over-allocation. Gas limit is vastly higher than consumption."
        ideal_limit = int(gas_used * 1.3)
        recommendations.append(f"Reduce gas limit to ~{ideal_limit:,} (1.3x actual usage).")
        recommendations.append("Use eth_estimateGas before submitting transactions.")
        recommendations.append("Check if wallet is using default high gas limits.")

    return {
        "score": score,
        "grade": grade,
        "assessment": assessment,
        "recommendations": recommendations,
    }


def _build_eip1559_analysis(tx_data: Dict) -> Dict[str, Any]:
    """Analyse EIP-1559 fields if present.

    Args:
        tx_data: Raw transaction data from Blockscout.

    Returns:
        EIP-1559 analysis dictionary.
    """
    max_fee = _safe_int(tx_data.get("max_fee_per_gas"))
    max_priority = _safe_int(tx_data.get("max_priority_fee_per_gas"))
    effective_price = _safe_int(tx_data.get("gas_price"))
    base_fee = tx_data.get("base_fee_per_gas")

    if not max_fee and not max_priority:
        return {
            "is_eip1559": False,
            "note": "Legacy transaction (Type 0). No EIP-1559 fields.",
        }

    result: Dict[str, Any] = {
        "is_eip1559": True,
        "max_fee_per_gas_gwei": _wei_to_gwei(max_fee) if max_fee else None,
        "max_priority_fee_per_gas_gwei": _wei_to_gwei(max_priority) if max_priority else None,
        "effective_gas_price_gwei": _wei_to_gwei(effective_price) if effective_price else None,
    }

    if base_fee is not None:
        base_fee_int = _safe_int(base_fee)
        result["base_fee_per_gas_gwei"] = _wei_to_gwei(base_fee_int)

    # Calculate savings from EIP-1559
    if max_fee and effective_price and max_fee > effective_price:
        savings_per_gas_wei = max_fee - effective_price
        gas_used = _safe_int(tx_data.get("gas_used"))
        if gas_used > 0:
            total_savings_wei = savings_per_gas_wei * gas_used
            result["savings_gwei"] = _wei_to_gwei(savings_per_gas_wei)
            result["total_savings_eth"] = round(_wei_to_eth(total_savings_wei), 8)
            result["note"] = (
                f"EIP-1559 saved you {result['total_savings_eth']:.8f} ETH "
                f"({result['savings_gwei']:.2f} Gwei/gas) vs max fee."
            )

    return result


def _compute_cost(tx_data: Dict, chain: str) -> Dict[str, Any]:
    """Compute the total transaction cost.

    Args:
        tx_data: Raw transaction data from Blockscout.
        chain: Canonical chain name.

    Returns:
        Cost breakdown dictionary.
    """
    gas_used = _safe_int(tx_data.get("gas_used"))
    gas_price = _safe_int(tx_data.get("gas_price"))
    gas_limit = _safe_int(tx_data.get("gas_limit", tx_data.get("gas")))
    native = CHAIN_NATIVE_CURRENCY.get(chain, "ETH")

    total_cost_wei = gas_used * gas_price
    total_cost_eth = _wei_to_eth(total_cost_wei)

    cost_at_limit_wei = gas_limit * gas_price if gas_limit > 0 else 0
    cost_at_limit_eth = _wei_to_eth(cost_at_limit_wei)

    savings_wei = cost_at_limit_wei - total_cost_wei
    savings_eth = _wei_to_eth(savings_wei)

    # Try to get USD price from tx_data (Blockscout sometimes includes it)
    exchange_rate = tx_data.get("exchange_rate")
    total_cost_usd = None
    if exchange_rate:
        try:
            rate = float(exchange_rate)
            total_cost_usd = round(total_cost_eth * rate, 4)
        except (ValueError, TypeError):
            pass

    result: Dict[str, Any] = {
        "total_cost_wei": str(total_cost_wei),
        "total_cost_native": round(total_cost_eth, 10),
        "native_currency": native,
        "cost_at_gas_limit_native": round(cost_at_limit_eth, 10),
        "savings_native": round(savings_eth, 10),
    }

    if total_cost_usd is not None:
        result["total_cost_usd"] = total_cost_usd

    return result


def _build_network_comparison(
    gas_used: int,
    gas_price: int,
    network_info: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare transaction gas usage with network averages.

    Args:
        gas_used: Gas consumed by the transaction.
        gas_price: Gas price in wei.
        network_info: Network stats from Blockscout.

    Returns:
        Comparison dictionary.
    """
    result: Dict[str, Any] = {}
    gas_price_gwei = _wei_to_gwei(gas_price)

    if not network_info.get("available"):
        result["note"] = "Network statistics unavailable for comparison."
        return result

    avg_price = network_info.get("avg_gas_price_gwei")
    if avg_price and avg_price > 0:
        result["network_avg_gas_price_gwei"] = avg_price
        diff_pct = ((gas_price_gwei - avg_price) / avg_price) * 100
        if diff_pct > 5:
            result["price_vs_average"] = f"{diff_pct:.0f}% above network average"
        elif diff_pct < -5:
            result["price_vs_average"] = f"{abs(diff_pct):.0f}% below network average"
        else:
            result["price_vs_average"] = "Close to network average"
    else:
        result["network_avg_gas_price_gwei"] = None

    # Compare gas usage vs simple transfer baseline
    usage_ratio = gas_used / SIMPLE_TRANSFER_GAS if SIMPLE_TRANSFER_GAS > 0 else 0
    if usage_ratio <= 1.0:
        result["usage_classification"] = "Simple transfer"
    elif usage_ratio <= 3.5:
        result["usage_classification"] = "Token operation (ERC-20/721)"
    elif usage_ratio <= 10:
        result["usage_classification"] = "DEX swap or moderate contract interaction"
    elif usage_ratio <= 50:
        result["usage_classification"] = "Complex DeFi operation"
    else:
        result["usage_classification"] = "Very complex operation or contract deployment"

    result["gas_used_vs_simple_transfer"] = f"{usage_ratio:.1f}x a simple ETH transfer"

    return result


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def profile_gas(tx_hash: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Profile gas usage for a transaction.

    Args:
        tx_hash: Transaction hash (0x + 64 hex).
        chain: Blockchain network name.

    Returns:
        Comprehensive gas profiling dictionary.
    """
    tx_hash = _validate_tx_hash(tx_hash)
    chain = _validate_chain(chain)
    chain_id = CHAIN_IDS.get(chain, "1")

    # Fetch transaction
    base_url = BLOCKSCOUT_CHAINS[chain]
    url = f"{base_url}/api/v2/transactions/{tx_hash}"
    tx_data = _fetch_json(url)
    if not tx_data:
        raise ValueError(
            f"Transaction {tx_hash} not found on {chain}. "
            "Verify the hash and chain are correct."
        )

    # Basic fields
    status = tx_data.get("status", "unknown")
    is_success = status == "ok" or tx_data.get("result") == "success"

    gas_used = _safe_int(tx_data.get("gas_used"))
    gas_limit = _safe_int(tx_data.get("gas_limit", tx_data.get("gas")))
    gas_price = _safe_int(tx_data.get("gas_price"))

    # Efficiency
    efficiency_pct = (gas_used / gas_limit * 100) if gas_limit > 0 else 0
    gas_wasted = gas_limit - gas_used if gas_limit > gas_used else 0

    gas_metrics: Dict[str, Any] = {
        "gas_used": gas_used,
        "gas_limit": gas_limit,
        "gas_price_gwei": round(_wei_to_gwei(gas_price), 4),
        "efficiency_percent": round(efficiency_pct, 2),
        "gas_wasted": gas_wasted,
    }

    # Effective gas price (may differ from gas_price for EIP-1559)
    effective_price = _safe_int(tx_data.get("gas_price"))
    if effective_price and effective_price != gas_price:
        gas_metrics["effective_gas_price_gwei"] = round(_wei_to_gwei(effective_price), 4)

    # EIP-1559 analysis
    eip1559 = _build_eip1559_analysis(tx_data)

    # Cost calculation
    cost = _compute_cost(tx_data, chain)

    # Network comparison
    network_stats = _fetch_network_stats(chain)
    network_info = _extract_network_gas_info(network_stats)
    comparison = _build_network_comparison(gas_used, gas_price, network_info)

    # Efficiency score
    efficiency = _compute_efficiency_score(gas_used, gas_limit)

    # Add gas price recommendation if above average
    avg_price = network_info.get("avg_gas_price_gwei")
    if avg_price and _wei_to_gwei(gas_price) > avg_price * 1.2:
        efficiency["recommendations"].append(
            f"Gas price was {_wei_to_gwei(gas_price):.2f} Gwei vs network average "
            f"{avg_price:.2f} Gwei. Consider using lower gas price for non-urgent transactions."
        )

    # Operation type guess
    op_type = _identify_operation_type(tx_data)

    return {
        "success": True,
        "scan_type": "gas_profile",
        "transaction": {
            "hash": tx_hash,
            "chain": chain,
            "chain_id": chain_id,
            "block_number": tx_data.get("block", tx_data.get("block_number")),
            "timestamp": tx_data.get("timestamp"),
            "status": status,
            "is_success": is_success,
            "operation_type": op_type,
        },
        "gas_metrics": gas_metrics,
        "eip1559": eip1559,
        "cost": cost,
        "network_comparison": comparison,
        "efficiency_score": efficiency,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point: read JSON from stdin, profile gas, write JSON to stdout."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({
                "success": False,
                "error": "No input provided. Send JSON via stdin.",
                "error_type": "VALIDATION_ERROR",
                "example": {"tx_hash": "0x...", "chain": "ethereum"},
            }))
            sys.exit(1)

        input_data = json.loads(raw)
        tx_hash = input_data.get("tx_hash", "")
        chain = input_data.get("chain", "ethereum")

        if not tx_hash:
            print(json.dumps({
                "success": False,
                "error": "Missing required parameter 'tx_hash'.",
                "error_type": "VALIDATION_ERROR",
                "suggestion": "Provide a transaction hash: {\"tx_hash\": \"0x...\", \"chain\": \"ethereum\"}",
            }))
            sys.exit(1)

        result = profile_gas(tx_hash, chain)
        print(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "Invalid JSON input.",
            "error_type": "VALIDATION_ERROR",
        }))
        sys.exit(1)
    except ValueError as exc:
        print(json.dumps({
            "success": False,
            "error": str(exc),
            "error_type": "VALIDATION_ERROR",
        }))
        sys.exit(1)
    except ConnectionError as exc:
        print(json.dumps({
            "success": False,
            "error": str(exc),
            "error_type": "API_ERROR",
            "suggestion": "Check your internet connection or try again shortly.",
        }))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {type(exc).__name__}: {exc}",
            "error_type": "INTERNAL_ERROR",
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
