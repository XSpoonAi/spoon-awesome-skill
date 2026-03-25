#!/usr/bin/env python3
"""
Etherscan Address Analysis Script
Fetches comprehensive address data from Etherscan API
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


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    """Fetch data from Etherscan-like API"""
    if api_key:
        params["apikey"] = api_key

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OnchainSkill/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

            if data.get("status") == "0" and "rate limit" in data.get("message", "").lower():
                raise ValueError("API rate limit exceeded. Please try again later.")

            return data
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def get_address_balance(address: str, chain: str) -> dict:
    """Get native token balance for an address"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        balance_wei = int(data.get("result", 0))
        balance = balance_wei / 1e18
        return {
            "balance_wei": str(balance_wei),
            "balance": balance,
            "symbol": config["native_symbol"]
        }

    return {"balance": 0, "symbol": config["native_symbol"]}


def get_transactions(address: str, chain: str, limit: int = 10) -> list:
    """Get recent transactions for an address"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        txs = data.get("result", [])
        return [
            {
                "hash": tx.get("hash"),
                "block": int(tx.get("blockNumber", 0)),
                "timestamp": int(tx.get("timeStamp", 0)),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value_wei": tx.get("value"),
                "value": float(tx.get("value", 0)) / 1e18,
                "gas_used": int(tx.get("gasUsed", 0)),
                "gas_price_gwei": int(tx.get("gasPrice", 0)) / 1e9,
                "is_error": tx.get("isError") == "1",
                "method_id": tx.get("methodId", "0x")
            }
            for tx in txs
        ]

    return []


def get_token_transfers(address: str, chain: str, limit: int = 10) -> list:
    """Get ERC20 token transfers for an address"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        transfers = data.get("result", [])
        return [
            {
                "hash": tx.get("hash"),
                "timestamp": int(tx.get("timeStamp", 0)),
                "token_name": tx.get("tokenName"),
                "token_symbol": tx.get("tokenSymbol"),
                "token_address": tx.get("contractAddress"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": float(tx.get("value", 0)) / (10 ** int(tx.get("tokenDecimal", 18))),
                "direction": "IN" if tx.get("to", "").lower() == address.lower() else "OUT"
            }
            for tx in transfers
        ]

    return []


def get_contract_info(address: str, chain: str) -> Optional[dict]:
    """Get contract information if address is a contract"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    # Check if address is a contract
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        result = data.get("result", [{}])[0]
        if result.get("ContractName"):
            return {
                "is_contract": True,
                "name": result.get("ContractName"),
                "compiler": result.get("CompilerVersion"),
                "verified": bool(result.get("SourceCode")),
                "proxy": result.get("Proxy") == "1",
                "implementation": result.get("Implementation") if result.get("Proxy") == "1" else None
            }

    return {"is_contract": False}


def analyze_address(address: str, chain: str) -> dict:
    """Comprehensive address analysis"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    # Validate address format
    if not address.startswith("0x") or len(address) != 42:
        raise ValueError(f"Invalid address format: {address}")

    # Fetch all data
    balance_data = get_address_balance(address, chain)
    transactions = get_transactions(address, chain, 10)
    token_transfers = get_token_transfers(address, chain, 10)
    contract_info = get_contract_info(address, chain)

    # Calculate statistics
    tx_count = len(transactions)
    total_received = sum(tx["value"] for tx in transactions if tx["to"].lower() == address.lower())
    total_sent = sum(tx["value"] for tx in transactions if tx["from"].lower() == address.lower())

    # Determine address type
    address_type = "Contract" if contract_info.get("is_contract") else "EOA (Wallet)"

    return {
        "success": True,
        "chain": chain,
        "address": address,
        "explorer_url": f"{config['explorer']}/address/{address}",
        "address_type": address_type,
        "balance": {
            "native": balance_data["balance"],
            "symbol": balance_data["symbol"],
            "native_wei": balance_data.get("balance_wei", "0")
        },
        "transaction_summary": {
            "total_transactions": tx_count,
            "total_received": round(total_received, 6),
            "total_sent": round(total_sent, 6),
            "recent_transactions": transactions[:5]
        },
        "token_activity": {
            "recent_transfers": token_transfers[:5]
        },
        "contract_info": contract_info if contract_info.get("is_contract") else None,
        "analysis": {
            "activity_level": "HIGH" if tx_count > 100 else "MEDIUM" if tx_count > 10 else "LOW",
            "net_flow": round(total_received - total_sent, 6)
        }
    }


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        address = input_data.get("address")
        chain = input_data.get("chain", "ethereum")

        if not address:
            print(json.dumps({"error": "Missing required parameter: address"}))
            sys.exit(1)

        result = analyze_address(address, chain)
        print(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
