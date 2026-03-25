#!/usr/bin/env python3
"""
Etherscan Transaction Analysis Script
Analyzes transaction details from Etherscan API
"""

import json
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional

# Chain configurations
CHAIN_CONFIG = {
    "ethereum": {
        "api_url": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://etherscan.io"
    },
    "polygon": {
        "api_url": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
        "native_symbol": "POL",  # Renamed from MATIC on Sept 4, 2024
        "explorer": "https://polygonscan.com"
    },
    "arbitrum": {
        "api_url": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://arbiscan.io"
    },
    "optimism": {
        "api_url": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://optimistic.etherscan.io"
    },
    "base": {
        "api_url": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://basescan.org"
    }
}

# Common function signatures
FUNCTION_SIGNATURES = {
    "0xa9059cbb": "transfer(address,uint256)",
    "0x095ea7b3": "approve(address,uint256)",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0x38ed1739": "swapExactTokensForTokens",
    "0x7ff36ab5": "swapExactETHForTokens",
    "0x18cbafe5": "swapExactTokensForETH",
    "0xe8e33700": "addLiquidity",
    "0xf305d719": "addLiquidityETH",
    "0xbaa2abde": "removeLiquidity",
    "0x02751cec": "removeLiquidityETH",
    "0x617ba037": "supply (Aave)",
    "0xa415bcad": "borrow (Aave)",
    "0x573ade81": "repay (Aave)",
    "0x69328dec": "withdraw (Aave)"
}


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    """Fetch data from Etherscan-like API"""
    if api_key:
        params["apikey"] = api_key

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TxAnalyzer/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def get_transaction_receipt(tx_hash: str, chain: str) -> dict:
    """Get transaction receipt"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "proxy",
        "action": "eth_getTransactionReceipt",
        "txhash": tx_hash
    }

    data = fetch_api(config["api_url"], params, api_key)
    return data.get("result", {})


def get_transaction_by_hash(tx_hash: str, chain: str) -> dict:
    """Get transaction details"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "proxy",
        "action": "eth_getTransactionByHash",
        "txhash": tx_hash
    }

    data = fetch_api(config["api_url"], params, api_key)
    return data.get("result", {})


def get_internal_transactions(tx_hash: str, chain: str) -> list:
    """Get internal transactions"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "txlistinternal",
        "txhash": tx_hash
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        return data.get("result", [])

    return []


def get_block_timestamp(block_number: int, chain: str) -> int:
    """Get block timestamp"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "block",
        "action": "getblockreward",
        "blockno": block_number
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        return int(data["result"].get("timeStamp", 0))

    return 0


def decode_function_signature(input_data: str) -> str:
    """Decode function signature from input data"""
    if not input_data or input_data == "0x":
        return "Native Transfer"

    method_id = input_data[:10].lower()
    return FUNCTION_SIGNATURES.get(method_id, f"Unknown ({method_id})")


def analyze_transaction(tx_hash: str, chain: str) -> dict:
    """Comprehensive transaction analysis"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    # Validate tx hash format
    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        raise ValueError(f"Invalid transaction hash format: {tx_hash}")

    # Fetch transaction data
    tx_data = get_transaction_by_hash(tx_hash, chain)
    if not tx_data:
        raise ValueError(f"Transaction not found: {tx_hash}")

    # Fetch receipt for additional info
    receipt = get_transaction_receipt(tx_hash, chain)

    # Fetch internal transactions
    internal_txs = get_internal_transactions(tx_hash, chain)

    # Parse basic info
    block_number = int(tx_data.get("blockNumber", "0x0"), 16)
    value_wei = int(tx_data.get("value", "0x0"), 16)
    gas_limit = int(tx_data.get("gas", "0x0"), 16)
    gas_price_wei = int(tx_data.get("gasPrice", "0x0"), 16)
    gas_used = int(receipt.get("gasUsed", "0x0"), 16) if receipt else 0

    # Calculate fees
    tx_fee_wei = gas_used * gas_price_wei
    tx_fee_eth = tx_fee_wei / 1e18

    # Determine status
    status = receipt.get("status", "0x1") if receipt else "0x1"
    is_success = status == "0x1"

    # Get timestamp
    timestamp = get_block_timestamp(block_number, chain)
    timestamp_str = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC") if timestamp else "Unknown"

    # Parse logs (events)
    logs = receipt.get("logs", []) if receipt else []
    events_count = len(logs)

    # Decode function
    input_data = tx_data.get("input", "0x")
    function_name = decode_function_signature(input_data)

    # Parse internal transactions
    internal_transfers = [
        {
            "from": itx.get("from"),
            "to": itx.get("to"),
            "value": float(itx.get("value", 0)) / 1e18,
            "type": itx.get("type", "call")
        }
        for itx in internal_txs[:10]  # Limit to 10
    ]

    return {
        "success": True,
        "chain": chain,
        "tx_hash": tx_hash,
        "explorer_url": f"{config['explorer']}/tx/{tx_hash}",
        "basic_info": {
            "block": block_number,
            "timestamp": timestamp_str,
            "status": "Success" if is_success else "Failed",
            "from": tx_data.get("from"),
            "to": tx_data.get("to"),
            "value": {
                "wei": str(value_wei),
                "native": value_wei / 1e18,
                "symbol": config["native_symbol"]
            }
        },
        "gas_info": {
            "gas_limit": gas_limit,
            "gas_used": gas_used,
            "gas_price_gwei": gas_price_wei / 1e9,
            "tx_fee": {
                "native": round(tx_fee_eth, 6),
                "symbol": config["native_symbol"]
            },
            "efficiency": f"{(gas_used / gas_limit * 100):.1f}%" if gas_limit > 0 else "N/A"
        },
        "function_info": {
            "function": function_name,
            "input_data_length": len(input_data),
            "events_emitted": events_count
        },
        "internal_transactions": {
            "count": len(internal_txs),
            "transfers": internal_transfers
        },
        "analysis": {
            "tx_type": classify_transaction(function_name, value_wei, logs),
            "complexity": "HIGH" if gas_used > 200000 else "MEDIUM" if gas_used > 50000 else "LOW"
        }
    }


def classify_transaction(function_name: str, value_wei: int, logs: list) -> str:
    """Classify transaction type"""
    func_lower = function_name.lower()

    if "transfer" in func_lower and "from" not in func_lower:
        return "Token Transfer"
    elif "approve" in func_lower:
        return "Token Approval"
    elif "swap" in func_lower:
        return "DEX Swap"
    elif "liquidity" in func_lower:
        return "Liquidity Operation"
    elif "supply" in func_lower or "deposit" in func_lower:
        return "Lending Deposit"
    elif "borrow" in func_lower:
        return "Lending Borrow"
    elif "repay" in func_lower:
        return "Loan Repayment"
    elif "withdraw" in func_lower:
        return "Withdrawal"
    elif "native transfer" in func_lower.lower():
        return "Native Token Transfer"
    elif len(logs) > 5:
        return "Complex DeFi Operation"
    else:
        return "Contract Interaction"


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        tx_hash = input_data.get("tx_hash")
        chain = input_data.get("chain", "ethereum")

        if not tx_hash:
            print(json.dumps({"error": "Missing required parameter: tx_hash"}))
            sys.exit(1)

        result = analyze_transaction(tx_hash, chain)
        print(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
