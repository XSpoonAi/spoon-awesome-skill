#!/usr/bin/env python3
"""
Token Approval Checker - Scan ERC20 approvals for an address and flag risks.
"""

import json
import sys
import os
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

# ERC20 Approval(address,address,uint256) topic0
APPROVAL_TOPIC = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3c925"
MAX_UINT256 = 2**256 - 1

CHAIN_CONFIG = {
    "ethereum": {
        "api_url": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
    },
    "polygon": {
        "api_url": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
    },
    "arbitrum": {
        "api_url": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
    },
    "optimism": {
        "api_url": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_API_KEY",
    },
    "base": {
        "api_url": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
    },
}

# Known safe spenders (DEX routers, etc.) - lowercase
KNOWN_SAFE_SPENDERS = {
    "ethereum": [
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # Uniswap Universal Router
        "0x1111111254eeb25477b68fb85ed929f73a960582",  # 1inch V5
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # 0x Exchange
    ],
    "polygon": [
        "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff",  # QuickSwap
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
    ],
    "arbitrum": [
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
        "0x1111111254eeb25477b68fb85ed929f73a960582",
    ],
    "optimism": [
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
    ],
    "base": [
        "0x2626664c2603336e57b271c5c0b26f421741e481",  # BaseSwap
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
    ],
}


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    if api_key:
        params["apikey"] = api_key
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TokenApprovalChecker/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        raise ConnectionError(f"API request failed: {e}")


def normalize_address(addr: str) -> str:
    return addr.lower().replace("0x", "").strip()


def get_token_list(api_url: str, address: str, api_key: Optional[str]) -> List[str]:
    """Get unique token contracts the address has interacted with via tokentx."""
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": "0",
        "endblock": "99999999",
        "sort": "desc",
        "page": "1",
        "offset": "100",
    }
    data = fetch_api(api_url, params, api_key)
    if data.get("status") != "1" or not data.get("result"):
        return []
    tokens = set()
    for tx in data["result"]:
        contract = tx.get("contractAddress")
        if contract:
            tokens.add(contract.lower())
    return list(tokens)


def get_approval_logs(
    api_url: str, token_address: str, owner_address: str, api_key: Optional[str]
) -> List[dict]:
    """Get Approval logs for owner on a given token contract."""
    owner_padded = "0x" + "0" * 24 + normalize_address(owner_address)
    params = {
        "module": "logs",
        "action": "getLogs",
        "address": token_address,
        "topic0": APPROVAL_TOPIC,
        "topic1": owner_padded,
        "fromBlock": "0",
        "toBlock": "99999999",
    }
    data = fetch_api(api_url, params, api_key)
    if data.get("status") != "1" or not data.get("result"):
        return []
    return data["result"]


def parse_approval_log(log: dict, token_address: str) -> Optional[dict]:
    """Parse Approval log to spender and value."""
    try:
        topics = log.get("topics", [])
        if len(topics) < 3:
            return None
        spender_hex = topics[2]
        if len(spender_hex) != 66:
            return None
        spender = "0x" + spender_hex[-40:].lower()
        data_hex = log.get("data", "0x0")
        if data_hex == "0x":
            value = 0
        else:
            value = int(data_hex, 16)
        return {
            "token_address": token_address.lower(),
            "spender": spender,
            "value": value,
            "unlimited": value >= MAX_UINT256 - (10**18),  # treat max as unlimited
        }
    except (ValueError, IndexError):
        return None


def get_latest_approval_per_spender(logs_parsed: List[dict]) -> List[dict]:
    """Keep only the latest approval per (token, spender) - by assuming logs are time-ordered."""
    seen = {}
    for item in logs_parsed:
        key = (item["token_address"], item["spender"])
        seen[key] = item
    return list(seen.values())


def assess_risk(approval: dict, chain: str) -> dict:
    """Add risk level and label."""
    safe_list = KNOWN_SAFE_SPENDERS.get(chain, [])
    spender_lower = approval["spender"].lower()
    is_known = spender_lower in [s.lower() for s in safe_list]
    risk = "low"
    if approval["unlimited"] and not is_known:
        risk = "high"
    elif approval["unlimited"] and is_known:
        risk = "medium"
    elif not is_known:
        risk = "medium"
    return {
        **approval,
        "risk": risk,
        "spender_known": is_known,
    }


def run_check(address: str, chain: str) -> Dict[str, Any]:
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")
    api_url = config["api_url"]
    addr = address if address.startswith("0x") else "0x" + address

    token_list = get_token_list(api_url, addr, api_key)
    if not token_list:
        return {
            "success": True,
            "address": addr,
            "chain": chain,
            "approvals": [],
            "summary": {"total": 0, "unlimited": 0, "high_risk": 0},
            "recommendations": ["No ERC20 approval records found, or this address has no token transfer history."],
        }

    all_approvals = []
    for token in token_list[:30]:  # limit to 30 tokens to avoid rate limit
        logs = get_approval_logs(api_url, token, addr, api_key)
        for log in logs:
            parsed = parse_approval_log(log, token)
            if parsed and parsed["value"] > 0:
                all_approvals.append(parsed)

    approvals_dedup = get_latest_approval_per_spender(all_approvals)
    with_risk = [assess_risk(a, chain) for a in approvals_dedup]

    unlimited_count = sum(1 for a in with_risk if a["unlimited"])
    high_risk_count = sum(1 for a in with_risk if a["risk"] == "high")

    recommendations = []
    if high_risk_count > 0:
        recommendations.append(
            f"Found {high_risk_count} high-risk approval(s) (unlimited + unknown spender). Consider revoking first."
        )
    if unlimited_count > 0 and high_risk_count < unlimited_count:
        recommendations.append(
            "Some approvals are unlimited. Consider revoking if you no longer use those DEXes/protocols."
        )
    if not recommendations:
        recommendations.append("Approvals are mostly to known protocols. Review periodically.")

    return {
        "success": True,
        "address": addr,
        "chain": chain,
        "approvals": with_risk,
        "summary": {
            "total": len(with_risk),
            "unlimited": unlimited_count,
            "high_risk": high_risk_count,
        },
        "recommendations": recommendations,
    }


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        address = input_data.get("address")
        chain = input_data.get("chain", "ethereum")

        if not address:
            print(json.dumps({"success": False, "error": "Missing required: address"}))
            sys.exit(1)

        result = run_check(address, chain)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "Invalid JSON input"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
