#!/usr/bin/env python3
"""
Smart Contract Analyzer Script
Analyzes smart contract code and security patterns
"""

import json
import sys
import os
import re
import urllib.request
import urllib.error
from typing import Optional, List, Dict

# Chain configurations
# Note: Etherscan API V1 is deprecated and will stop working on August 15, 2025
# Consider migrating to V2 API: https://api.etherscan.io/v2/api?chainid={CHAIN_ID}
# RPC URLs sourced from Chainlist.org (https://chainlist.org)
CHAIN_CONFIG = {
    "ethereum": {
        "rpc_url": "https://eth.llamarpc.com",
        "api_url": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "explorer": "https://etherscan.io"
    },
    "polygon": {
        "rpc_url": "https://polygon-rpc.com",
        "api_url": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
        "explorer": "https://polygonscan.com"
    },
    "arbitrum": {
        "rpc_url": "https://arb1.arbitrum.io/rpc",
        "api_url": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
        "explorer": "https://arbiscan.io"
    },
    "optimism": {
        "rpc_url": "https://mainnet.optimism.io",
        "api_url": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_API_KEY",
        "explorer": "https://optimistic.etherscan.io"
    },
    "base": {
        "rpc_url": "https://mainnet.base.org",
        "api_url": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
        "explorer": "https://basescan.org"
    },
    "bsc": {
        "rpc_url": "https://bsc-dataseed.bnbchain.org",
        "api_url": "https://api.bscscan.com/api",
        "api_key_env": "BSCSCAN_API_KEY",
        "explorer": "https://bscscan.com"
    },
    "zksync": {
        "rpc_url": "https://mainnet.era.zksync.io",
        "api_url": "https://block-explorer-api.mainnet.zksync.io/api",
        "api_key_env": "ZKSYNC_API_KEY",
        "explorer": "https://explorer.zksync.io"
    },
    "linea": {
        "rpc_url": "https://rpc.linea.build",
        "api_url": "https://api.lineascan.build/api",
        "api_key_env": "LINEASCAN_API_KEY",
        "explorer": "https://lineascan.build"
    },
    "neox": {
        "rpc_url": "https://mainnet-1.rpc.banelabs.org",
        "api_url": "https://xexplorer.neo.org/api",
        "api_key_env": "NEOX_API_KEY",
        "explorer": "https://xexplorer.neo.org"
    }
}

# Security patterns to check
SECURITY_PATTERNS = {
    "reentrancy_guard": {
        "pattern": r"(ReentrancyGuard|nonReentrant|_status|_notEntered)",
        "description": "Reentrancy protection",
        "severity": "HIGH",
        "good": True
    },
    "access_control": {
        "pattern": r"(Ownable|AccessControl|onlyOwner|onlyRole|hasRole)",
        "description": "Access control mechanism",
        "severity": "HIGH",
        "good": True
    },
    "pausable": {
        "pattern": r"(Pausable|whenNotPaused|_pause|_unpause)",
        "description": "Emergency pause functionality",
        "severity": "MEDIUM",
        "good": True
    },
    "upgradeable": {
        "pattern": r"(Upgradeable|UUPSUpgradeable|TransparentUpgradeableProxy|initializer)",
        "description": "Upgradeable contract pattern",
        "severity": "INFO",
        "good": None  # Neutral - depends on context
    },
    "selfdestruct": {
        "pattern": r"selfdestruct|suicide",
        "description": "Self-destruct capability (potential risk)",
        "severity": "HIGH",
        "good": False
    },
    "delegatecall": {
        "pattern": r"delegatecall",
        "description": "Delegatecall usage (review carefully)",
        "severity": "MEDIUM",
        "good": None
    },
    "tx_origin": {
        "pattern": r"tx\.origin",
        "description": "tx.origin usage (phishing vulnerability)",
        "severity": "HIGH",
        "good": False
    },
    "unchecked_call": {
        "pattern": r"\.call\{|\.call\(|\.send\(",
        "description": "Low-level call (check return value)",
        "severity": "MEDIUM",
        "good": None
    },
    "safemath": {
        "pattern": r"(SafeMath|unchecked\s*\{)",
        "description": "Arithmetic safety",
        "severity": "LOW",
        "good": None
    },
    "hardcoded_address": {
        "pattern": r"0x[a-fA-F0-9]{40}(?!\s*\))",
        "description": "Hardcoded addresses",
        "severity": "INFO",
        "good": None
    }
}


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    """Fetch data from Etherscan-like API"""
    if api_key:
        params["apikey"] = api_key

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ContractAnalyzer/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def get_contract_source(address: str, chain: str) -> dict:
    """Get contract source code from Etherscan"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1" and data.get("result"):
        return data["result"][0]

    return {}


def get_contract_abi(address: str, chain: str) -> list:
    """Get contract ABI from Etherscan"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "contract",
        "action": "getabi",
        "address": address
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1" and data.get("result"):
        try:
            return json.loads(data["result"])
        except json.JSONDecodeError:
            return []

    return []


def analyze_security_patterns(source_code: str) -> List[Dict]:
    """Analyze source code for security patterns"""
    findings = []

    for pattern_name, pattern_info in SECURITY_PATTERNS.items():
        matches = re.findall(pattern_info["pattern"], source_code, re.IGNORECASE)

        if matches:
            findings.append({
                "pattern": pattern_name,
                "description": pattern_info["description"],
                "severity": pattern_info["severity"],
                "found": True,
                "is_positive": pattern_info["good"],
                "occurrences": len(matches)
            })

    return findings


def extract_functions_from_abi(abi: list) -> List[Dict]:
    """Extract function information from ABI"""
    functions = []

    for item in abi:
        if item.get("type") == "function":
            func_info = {
                "name": item.get("name", "unknown"),
                "state_mutability": item.get("stateMutability", "nonpayable"),
                "inputs": len(item.get("inputs", [])),
                "outputs": len(item.get("outputs", [])),
                "is_view": item.get("stateMutability") in ["view", "pure"],
                "is_payable": item.get("stateMutability") == "payable"
            }
            functions.append(func_info)

    return functions


def identify_admin_functions(functions: List[Dict], source_code: str) -> List[str]:
    """Identify potential admin/privileged functions"""
    admin_keywords = [
        "owner", "admin", "set", "update", "change", "modify",
        "pause", "unpause", "mint", "burn", "upgrade", "transfer",
        "withdraw", "emergency", "rescue"
    ]

    admin_functions = []

    for func in functions:
        name_lower = func["name"].lower()
        if any(keyword in name_lower for keyword in admin_keywords):
            if not func["is_view"]:
                admin_functions.append(func["name"])

    return admin_functions


def calculate_risk_score(findings: List[Dict], is_verified: bool, is_proxy: bool) -> Dict:
    """Calculate overall risk score"""
    score = 100  # Start with perfect score

    # Deduct for negative findings
    for finding in findings:
        if finding["found"]:
            if finding["is_positive"] is False:
                if finding["severity"] == "HIGH":
                    score -= 20
                elif finding["severity"] == "MEDIUM":
                    score -= 10
                else:
                    score -= 5

    # Bonus for positive security patterns
    for finding in findings:
        if finding["found"] and finding["is_positive"] is True:
            score += 5

    # Deduct if not verified
    if not is_verified:
        score -= 30

    # Note proxy status (not necessarily bad, but noteworthy)
    if is_proxy:
        score -= 5

    # Clamp score
    score = max(0, min(100, score))

    # Determine risk level
    if score >= 80:
        risk_level = "LOW"
    elif score >= 60:
        risk_level = "MEDIUM"
    elif score >= 40:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return {
        "score": score,
        "risk_level": risk_level
    }


def analyze_contract(address: str, chain: str) -> dict:
    """Comprehensive contract analysis"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")

    # Validate address format
    if not address.startswith("0x") or len(address) != 42:
        raise ValueError(f"Invalid address format: {address}")

    # Fetch contract source
    source_info = get_contract_source(address, chain)

    if not source_info:
        return {
            "success": True,
            "chain": chain,
            "address": address,
            "is_contract": False,
            "note": "Address is not a contract or contract source is not available"
        }

    contract_name = source_info.get("ContractName", "Unknown")
    is_verified = bool(source_info.get("SourceCode"))
    is_proxy = source_info.get("Proxy") == "1"
    implementation = source_info.get("Implementation") if is_proxy else None
    compiler_version = source_info.get("CompilerVersion", "Unknown")
    source_code = source_info.get("SourceCode", "")

    # Get ABI
    abi = get_contract_abi(address, chain)

    # Analyze security patterns (if source is available)
    security_findings = []
    if source_code:
        security_findings = analyze_security_patterns(source_code)

    # Extract functions from ABI
    functions = extract_functions_from_abi(abi)
    admin_functions = identify_admin_functions(functions, source_code)

    # Calculate risk score
    risk_assessment = calculate_risk_score(security_findings, is_verified, is_proxy)

    # Count function types
    view_functions = [f for f in functions if f["is_view"]]
    write_functions = [f for f in functions if not f["is_view"]]
    payable_functions = [f for f in functions if f["is_payable"]]

    return {
        "success": True,
        "chain": chain,
        "address": address,
        "explorer_url": f"{config['explorer']}/address/{address}",
        "contract_info": {
            "name": contract_name,
            "compiler": compiler_version,
            "verified": is_verified,
            "is_proxy": is_proxy,
            "implementation": implementation,
            "source_lines": len(source_code.split("\n")) if source_code else 0
        },
        "function_analysis": {
            "total_functions": len(functions),
            "view_functions": len(view_functions),
            "write_functions": len(write_functions),
            "payable_functions": len(payable_functions),
            "admin_functions": admin_functions[:10]  # Limit display
        },
        "security_analysis": {
            "findings": security_findings,
            "positive_patterns": [f for f in security_findings if f.get("is_positive") is True],
            "concerns": [f for f in security_findings if f.get("is_positive") is False]
        },
        "risk_assessment": {
            "score": risk_assessment["score"],
            "level": risk_assessment["risk_level"],
            "verified_bonus": "Yes" if is_verified else "No (major concern)",
            "recommendation": get_recommendation(risk_assessment["risk_level"], is_verified, is_proxy)
        }
    }


def get_recommendation(risk_level: str, is_verified: bool, is_proxy: bool) -> str:
    """Get recommendation based on analysis"""
    if not is_verified:
        return "CAUTION: Contract source is not verified. Consider this high risk for interaction."

    if risk_level == "CRITICAL":
        return "HIGH RISK: Multiple security concerns detected. Avoid interaction unless you understand the risks."
    elif risk_level == "HIGH":
        return "ELEVATED RISK: Some security concerns present. Review carefully before interacting."
    elif risk_level == "MEDIUM":
        return "MODERATE RISK: Generally safe patterns but some areas need attention. Proceed with caution."
    else:
        if is_proxy:
            return "LOW RISK: Contract follows good security practices. Note: Proxy pattern means implementation can be upgraded."
        return "LOW RISK: Contract follows good security practices. Standard caution still advised."


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        address = input_data.get("address")
        chain = input_data.get("chain", "ethereum")

        if not address:
            print(json.dumps({"error": "Missing required parameter: address"}))
            sys.exit(1)

        result = analyze_contract(address, chain)
        print(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
