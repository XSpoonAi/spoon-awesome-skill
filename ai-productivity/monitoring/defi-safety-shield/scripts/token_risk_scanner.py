#!/usr/bin/env python3
"""
Token Risk Scanner
Comprehensive token security analysis combining GoPlus Security and Honeypot.is APIs.
Detects honeypots, rug pulls, high taxes, dangerous contract functions, and more.

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error
import re

GOPLUS_API = "https://api.gopluslabs.io/api/v1"
HONEYPOT_API = "https://api.honeypot.is/v2"

CHAIN_IDS = {
    "ethereum": "1",
    "eth": "1",
    "bsc": "56",
    "bnb": "56",
    "polygon": "137",
    "matic": "137",
    "arbitrum": "42161",
    "arb": "42161",
    "base": "8453",
    "optimism": "10",
    "op": "10",
    "avalanche": "43114",
    "avax": "43114",
    "linea": "59144",
    "zksync": "324",
}

# Chains supported by Honeypot.is
HONEYPOT_CHAINS = {"1", "56", "137", "42161", "8453", "10", "43114"}


def fetch_json(url: str, timeout: int = 20) -> dict:
    """Fetch JSON data from URL with error handling."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DeFiSafetyShield/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise ConnectionError(
                "Rate limit exceeded. Please wait 1-2 minutes before retrying."
            )
        raise ConnectionError(f"API error (HTTP {e.code})")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Connection failed: {e.reason}")


def validate_address(address: str) -> str:
    """Validate and normalize an Ethereum-style address."""
    address = address.strip()
    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        raise ValueError(
            f"Invalid address format: {address}. "
            "Expected 0x followed by 40 hex characters."
        )
    return address.lower()


def validate_chain(chain: str) -> str:
    """Validate chain and return chain ID."""
    chain_lower = chain.lower().strip()
    chain_id = CHAIN_IDS.get(chain_lower)
    if not chain_id:
        raise ValueError(
            f"Unsupported chain: {chain}. "
            f"Supported: {', '.join(sorted(set(CHAIN_IDS.keys())))}"
        )
    return chain_id


def fetch_goplus_security(token_address: str, chain_id: str) -> dict:
    """Fetch token security data from GoPlus."""
    url = (
        f"{GOPLUS_API}/token_security/{chain_id}"
        f"?contract_addresses={token_address}"
    )
    data = fetch_json(url)

    if data.get("code") != 1:
        raise ValueError(f"GoPlus API error: {data.get('message', 'Unknown')}")

    result = data.get("result", {})
    token_data = result.get(token_address, {})
    if not token_data:
        raise ValueError(
            f"Token not found on chain {chain_id}. "
            "Verify the address and chain are correct."
        )
    return token_data


def fetch_honeypot_check(token_address: str, chain_id: str) -> dict:
    """Fetch honeypot analysis from Honeypot.is."""
    if chain_id not in HONEYPOT_CHAINS:
        return {"supported": False}

    url = f"{HONEYPOT_API}/IsHoneypot?address={token_address}&chainID={chain_id}"
    try:
        data = fetch_json(url)
        data["supported"] = True
        return data
    except ConnectionError:
        return {"supported": False, "error": "Honeypot.is unavailable"}


def calculate_risk_score(goplus: dict, honeypot: dict) -> dict:
    """Calculate composite risk score from security data."""
    score = 0
    flags: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # Critical risks (each adds 3-4 points)
    if goplus.get("is_honeypot") == "1":
        score += 4
        flags.append("HONEYPOT: Cannot sell tokens after buying")

    if honeypot.get("supported") and honeypot.get("honeypotResult", {}).get(
        "isHoneypot"
    ):
        score += 4
        flags.append("HONEYPOT CONFIRMED by Honeypot.is simulation")

    if goplus.get("hidden_owner") == "1":
        score += 3
        flags.append("Hidden owner detected — ownership obfuscated")

    if goplus.get("can_take_back_ownership") == "1":
        score += 3
        flags.append("Owner can reclaim ownership after renouncing")

    if goplus.get("selfdestruct") == "1":
        score += 3
        flags.append("Self-destruct function — contract can be destroyed")

    if goplus.get("owner_change_balance") == "1":
        score += 3
        flags.append("Owner can modify token balances")

    honeypot_creator = goplus.get("honeypot_with_same_creator")
    if honeypot_creator and honeypot_creator != "0":
        score += 3
        flags.append("Creator has deployed honeypot tokens before")

    # High risks (each adds 2 points)
    sell_tax = float(goplus.get("sell_tax", "0") or "0") * 100
    buy_tax = float(goplus.get("buy_tax", "0") or "0") * 100

    if sell_tax > 50:
        score += 3
        flags.append(f"EXTREME sell tax: {sell_tax:.1f}%")
    elif sell_tax > 10:
        score += 2
        warnings.append(f"High sell tax: {sell_tax:.1f}%")
    elif sell_tax > 5:
        score += 1
        warnings.append(f"Moderate sell tax: {sell_tax:.1f}%")

    if buy_tax > 50:
        score += 3
        flags.append(f"EXTREME buy tax: {buy_tax:.1f}%")
    elif buy_tax > 10:
        score += 2
        warnings.append(f"High buy tax: {buy_tax:.1f}%")
    elif buy_tax > 5:
        score += 1
        warnings.append(f"Moderate buy tax: {buy_tax:.1f}%")

    if goplus.get("is_blacklisted") == "1":
        score += 2
        warnings.append("Token has blacklist function")

    if goplus.get("transfer_pausable") == "1":
        score += 2
        warnings.append("Transfers can be paused by owner")

    if goplus.get("slippage_modifiable") == "1":
        score += 2
        warnings.append("Owner can modify tax rates")

    if goplus.get("cannot_sell_all") == "1":
        score += 2
        warnings.append("Cannot sell entire position at once")

    if goplus.get("trading_cooldown") == "1":
        score += 1
        warnings.append("Trading cooldown enforced between trades")

    if goplus.get("is_anti_whale") == "1":
        score += 0  # This can be legitimate
        info.append("Anti-whale mechanism active (max tx limits)")

    # Medium risks (each adds 1 point)
    if goplus.get("is_mintable") == "1":
        score += 1
        warnings.append("Token is mintable — supply can be increased")

    if goplus.get("is_proxy") == "1":
        score += 1
        warnings.append("Proxy contract — code can be upgraded")

    if goplus.get("external_call") == "1":
        score += 1
        warnings.append("Contract makes external calls")

    if goplus.get("is_open_source") != "1":
        score += 2
        warnings.append("Contract source code NOT verified")

    # Positive signals (reduce score)
    if goplus.get("is_open_source") == "1":
        info.append("Contract source code is verified")

    if goplus.get("is_in_dex") == "1":
        info.append("Token is listed on DEX")

    trust = goplus.get("trust_list")
    if trust == "1":
        score = max(0, score - 3)
        info.append("Token is on GoPlus trusted list")

    # Cap at 10
    score = min(score, 10)

    # Determine level
    if score >= 8:
        level = "CRITICAL"
    elif score >= 6:
        level = "HIGH"
    elif score >= 4:
        level = "MEDIUM"
    elif score >= 2:
        level = "LOW"
    else:
        level = "SAFE"

    return {
        "score": score,
        "level": level,
        "critical_flags": flags,
        "warnings": warnings,
        "info": info,
    }


def scan_token(token_address: str, chain: str = "ethereum") -> dict:
    """Run comprehensive token security scan."""
    token_address = validate_address(token_address)
    chain_id = validate_chain(chain)

    # Fetch from both APIs
    goplus = fetch_goplus_security(token_address, chain_id)
    honeypot = fetch_honeypot_check(token_address, chain_id)

    # Calculate risk
    risk = calculate_risk_score(goplus, honeypot)

    # Extract key metrics
    sell_tax = float(goplus.get("sell_tax", "0") or "0") * 100
    buy_tax = float(goplus.get("buy_tax", "0") or "0") * 100

    # Holder analysis
    holders = goplus.get("holders", [])
    top_holders = []
    for h in holders[:5]:
        top_holders.append(
            {
                "address": h.get("address", "")[:10] + "...",
                "percent": round(float(h.get("percent", 0)) * 100, 2),
                "is_locked": h.get("is_locked") == "1",
                "tag": h.get("tag", ""),
            }
        )

    # DEX info
    dex_list = goplus.get("dex", [])
    dex_info = []
    for d in dex_list[:3]:
        dex_info.append(
            {
                "name": d.get("name", "Unknown"),
                "liquidity": d.get("liquidity", "0"),
                "pair": d.get("pair", ""),
            }
        )

    # Honeypot simulation data
    honeypot_sim = {}
    if honeypot.get("supported"):
        sim = honeypot.get("simulationResult", {})
        honeypot_sim = {
            "is_honeypot": honeypot.get("honeypotResult", {}).get(
                "isHoneypot", False
            ),
            "buy_tax_simulated": round(sim.get("buyTax", 0), 2),
            "sell_tax_simulated": round(sim.get("sellTax", 0), 2),
            "buy_gas": sim.get("buyGas"),
            "sell_gas": sim.get("sellGas"),
        }

    return {
        "success": True,
        "scan_type": "token_risk",
        "token": {
            "address": token_address,
            "name": goplus.get("token_name", "Unknown"),
            "symbol": goplus.get("token_symbol", "Unknown"),
            "chain": chain,
            "chain_id": chain_id,
        },
        "risk_assessment": risk,
        "taxes": {
            "buy_tax_percent": round(buy_tax, 2),
            "sell_tax_percent": round(sell_tax, 2),
        },
        "contract_security": {
            "is_open_source": goplus.get("is_open_source") == "1",
            "is_proxy": goplus.get("is_proxy") == "1",
            "is_mintable": goplus.get("is_mintable") == "1",
            "has_self_destruct": goplus.get("selfdestruct") == "1",
            "hidden_owner": goplus.get("hidden_owner") == "1",
            "can_take_back_ownership": goplus.get("can_take_back_ownership") == "1",
            "owner_can_change_balance": goplus.get("owner_change_balance") == "1",
            "is_blacklisted": goplus.get("is_blacklisted") == "1",
            "transfer_pausable": goplus.get("transfer_pausable") == "1",
            "slippage_modifiable": goplus.get("slippage_modifiable") == "1",
        },
        "holder_analysis": {
            "total_holders": goplus.get("holder_count", "Unknown"),
            "top_holders": top_holders,
            "creator_address": goplus.get("creator_address", "Unknown"),
            "creator_percent": round(
                float(goplus.get("creator_percent", 0) or 0) * 100, 2
            ),
            "owner_percent": round(
                float(goplus.get("owner_percent", 0) or 0) * 100, 2
            ),
        },
        "liquidity": {"dex_listed": goplus.get("is_in_dex") == "1", "dex": dex_info},
        "honeypot_simulation": honeypot_sim if honeypot_sim else None,
    }


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        token_address = input_data.get("token_address", "")
        chain = input_data.get("chain", "ethereum")

        if not token_address:
            print(
                json.dumps(
                    {
                        "error": "Provide 'token_address' parameter",
                        "example": {
                            "token_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                            "chain": "ethereum",
                        },
                    }
                )
            )
            sys.exit(1)

        result = scan_token(token_address, chain)
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
