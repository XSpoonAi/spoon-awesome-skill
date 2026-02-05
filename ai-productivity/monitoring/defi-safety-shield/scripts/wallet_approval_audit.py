#!/usr/bin/env python3
"""
Wallet Approval Auditor
Audits ERC-20 token approvals for a wallet address using GoPlus Security API v2.
Identifies unlimited approvals, risky spenders, and provides revoke recommendations.

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error
import re

GOPLUS_API_V1 = "https://api.gopluslabs.io/api/v1"
GOPLUS_API_V2 = "https://api.gopluslabs.io/api/v2"

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


def check_address_security(address: str) -> dict:
    """Check if the wallet address itself has any security flags."""
    url = f"{GOPLUS_API_V1}/address_security/{address}"
    try:
        data = fetch_json(url)
        if data.get("code") == 1:
            return data.get("result", {})
    except ConnectionError:
        pass
    return {}


def fetch_token_approvals(wallet_address: str, chain_id: str) -> list:
    """Fetch ERC-20 token approvals for a wallet from GoPlus v2."""
    url = (
        f"{GOPLUS_API_V2}/token_approval_security/{chain_id}"
        f"?addresses={wallet_address}"
    )
    data = fetch_json(url)

    if data.get("code") != 1:
        msg = data.get("message", "Unknown error")
        if "no data" in msg.lower():
            return []
        raise ValueError(f"GoPlus API error: {msg}")

    result = data.get("result", [])

    # API may return a list directly or a dict keyed by address
    if isinstance(result, list):
        return result
    elif isinstance(result, dict):
        wallet_data = result.get(wallet_address, result.get(wallet_address.lower(), {}))
        if isinstance(wallet_data, list):
            return wallet_data
        elif isinstance(wallet_data, dict):
            return wallet_data.get("token_approval_list", [])
    return []


def analyze_approvals(approvals: list) -> dict:
    """Analyze token approvals for risks."""
    total = len(approvals)
    risky_count = 0
    unlimited_count = 0
    malicious_count = 0
    analyzed: list[dict] = []

    for approval in approvals:
        risk_level = "LOW"
        risks: list[str] = []

        # Check for unlimited approval
        approved_amount = approval.get("approved_amount", "0")
        if approved_amount == "unlimited" or (
            isinstance(approved_amount, str)
            and len(approved_amount) > 60
        ):
            unlimited_count += 1
            risks.append("Unlimited approval — spender can drain all tokens")
            risk_level = "MEDIUM"

        # Check spender contract risk
        spender_info = approval.get("approved_contract", {})
        if isinstance(spender_info, dict):
            if spender_info.get("is_open_source") == 0:
                risks.append("Spender contract is NOT open source")
                risk_level = "HIGH"

            if spender_info.get("malicious_behavior"):
                malicious_count += 1
                risks.append("Spender has MALICIOUS behavior detected")
                risk_level = "CRITICAL"

            if spender_info.get("doubt_list") == 1:
                risks.append("Spender is on doubt/suspicious list")
                risk_level = "HIGH"

            trust = spender_info.get("trust_list")
            if trust == 1:
                if not risks:
                    risk_level = "SAFE"

        if risk_level in ("HIGH", "CRITICAL"):
            risky_count += 1

        token_name = approval.get("token_name", "Unknown")
        token_symbol = approval.get("token_symbol", "Unknown")
        spender_address = approval.get("approved_spender", "Unknown")

        analyzed.append({
            "token": f"{token_name} ({token_symbol})",
            "token_address": approval.get("token_address", "Unknown"),
            "spender": spender_address[:10] + "..." if len(str(spender_address)) > 10 else spender_address,
            "spender_name": (
                spender_info.get("contract_name", "Unknown")
                if isinstance(spender_info, dict)
                else "Unknown"
            ),
            "approved_amount": (
                "UNLIMITED" if approved_amount == "unlimited" or (
                    isinstance(approved_amount, str) and len(approved_amount) > 60
                ) else approved_amount
            ),
            "risk_level": risk_level,
            "risks": risks,
        })

    # Sort by risk level (CRITICAL first)
    risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "SAFE": 4}
    analyzed.sort(key=lambda x: risk_order.get(x["risk_level"], 5))

    return {
        "total_approvals": total,
        "unlimited_approvals": unlimited_count,
        "risky_approvals": risky_count,
        "malicious_spenders": malicious_count,
        "approvals": analyzed[:20],  # Limit to top 20
    }


def audit_wallet(wallet_address: str, chain: str = "ethereum") -> dict:
    """Run comprehensive wallet approval audit."""
    wallet_address = validate_address(wallet_address)
    chain_id = validate_chain(chain)

    # Check wallet address security
    address_security = check_address_security(wallet_address)
    address_flags: list[str] = []
    for key, label in [
        ("phishing_activities", "Phishing activity detected"),
        ("cybercrime", "Associated with cybercrime"),
        ("money_laundering", "Money laundering flag"),
        ("stealing_attack", "Theft attack involvement"),
        ("blackmail_activities", "Blackmail activity"),
    ]:
        if address_security.get(key) == "1":
            address_flags.append(label)

    # Fetch and analyze approvals
    approvals = fetch_token_approvals(wallet_address, chain_id)
    analysis = analyze_approvals(approvals)

    # Calculate overall risk
    score = 0
    if analysis["malicious_spenders"] > 0:
        score += 4
    if analysis["unlimited_approvals"] > 5:
        score += 2
    elif analysis["unlimited_approvals"] > 0:
        score += 1
    if analysis["risky_approvals"] > 3:
        score += 2
    elif analysis["risky_approvals"] > 0:
        score += 1
    if address_flags:
        score += 3

    score = min(score, 10)

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

    # Generate recommendations
    recommendations: list[str] = []
    if analysis["malicious_spenders"] > 0:
        recommendations.append(
            "URGENT: Revoke approvals to malicious spender contracts immediately"
        )
    if analysis["unlimited_approvals"] > 0:
        recommendations.append(
            f"Revoke or reduce {analysis['unlimited_approvals']} unlimited approval(s)"
        )
    if analysis["risky_approvals"] > 0:
        recommendations.append(
            f"Review {analysis['risky_approvals']} high-risk approval(s)"
        )
    if not recommendations:
        recommendations.append("No immediate action required — approvals look safe")

    return {
        "success": True,
        "scan_type": "wallet_approval_audit",
        "wallet": {
            "address": wallet_address,
            "chain": chain,
            "chain_id": chain_id,
        },
        "address_security": {
            "flags": address_flags if address_flags else None,
            "is_contract": address_security.get("contract_address") == "1",
        },
        "risk_assessment": {
            "score": score,
            "level": level,
        },
        "approval_analysis": analysis,
        "recommendations": recommendations,
    }


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        wallet_address = input_data.get("wallet_address", "")
        chain = input_data.get("chain", "ethereum")

        if not wallet_address:
            print(
                json.dumps(
                    {
                        "error": "Provide 'wallet_address' parameter",
                        "example": {
                            "wallet_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                            "chain": "ethereum",
                        },
                    }
                )
            )
            sys.exit(1)

        result = audit_wallet(wallet_address, chain)
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
