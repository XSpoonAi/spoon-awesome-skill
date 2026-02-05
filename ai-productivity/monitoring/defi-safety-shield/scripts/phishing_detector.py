#!/usr/bin/env python3
"""
Phishing Detector
Detects phishing websites and verifies dApp security using GoPlus Security API.
Checks URLs against known phishing databases and analyzes associated smart contracts.

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
import re

GOPLUS_API = "https://api.gopluslabs.io/api/v1"


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


def validate_url(url: str) -> str:
    """Validate and normalize URL input."""
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")
    if len(url) > 2048:
        raise ValueError("URL too long (max 2048 characters)")

    # Add https:// if no scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Basic URL validation
    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    # Check for suspicious characters
    if any(c in url for c in ["<", ">", "{", "}", "|", "\\", "^", "`"]):
        raise ValueError("URL contains invalid characters")

    return url


def check_phishing(url: str) -> dict:
    """Check if URL is a known phishing site via GoPlus."""
    encoded_url = urllib.parse.quote(url, safe="")
    api_url = f"{GOPLUS_API}/phishing_site?url={encoded_url}"

    data = fetch_json(api_url)

    if data.get("code") != 1:
        raise ValueError(f"GoPlus API error: {data.get('message', 'Unknown')}")

    result = data.get("result", {})
    is_phishing = result.get("phishing_site") == 1

    return {
        "is_phishing": is_phishing,
        "website_contract_security": result.get("website_contract_security", []),
    }


def check_dapp_security(url: str) -> dict:
    """Check dApp security status via GoPlus."""
    encoded_url = urllib.parse.quote(url, safe="")
    api_url = f"{GOPLUS_API}/dapp_security?url={encoded_url}"

    try:
        data = fetch_json(api_url)

        if data.get("code") != 1:
            return {"available": False}

        result = data.get("result", {})
        if not result:
            return {"available": False}

        # Extract contract security info
        contracts = []
        for cs in result.get("contracts_security", []):
            chain_id = cs.get("chain_id", "")
            for contract in cs.get("contracts", []):
                contracts.append({
                    "chain_id": chain_id,
                    "address": contract.get("contract_address", ""),
                    "is_open_source": contract.get("is_open_source") == 1,
                    "malicious": contract.get("malicious_contract") == 1,
                    "creator_malicious": contract.get("malicious_creator") == 1,
                })

        # Extract audit info
        audits = []
        for audit in result.get("audit_info", []):
            audits.append({
                "firm": audit.get("audit_firm", "Unknown"),
                "link": audit.get("audit_link", ""),
            })

        return {
            "available": True,
            "project_name": result.get("project_name", "Unknown"),
            "is_audited": result.get("is_audit") == 1,
            "is_trusted": result.get("trust_list") == 1,
            "audits": audits,
            "contracts": contracts[:10],  # Limit to 10
        }

    except ConnectionError:
        return {"available": False}


def analyze_url_patterns(url: str) -> list[str]:
    """Analyze URL for common phishing patterns."""
    warnings: list[str] = []
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()

    # Known legitimate domains for comparison
    legit_domains = [
        "uniswap.org",
        "aave.com",
        "compound.finance",
        "curve.fi",
        "lido.fi",
        "opensea.io",
        "metamask.io",
        "etherscan.io",
        "coingecko.com",
    ]

    # Check for suspicious TLDs
    suspicious_tlds = [".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".buzz"]
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            warnings.append(f"Suspicious TLD: {tld}")
            break

    # Check for typosquatting patterns
    for legit in legit_domains:
        legit_base = legit.split(".")[0]
        domain_base = domain.split(".")[0].replace("www.", "")
        if legit_base != domain_base and (
            legit_base in domain_base or domain_base in legit_base
        ):
            if domain != legit and not domain.endswith("." + legit):
                warnings.append(
                    f"Domain resembles {legit} — possible typosquat"
                )

    # Check for excessive subdomains
    subdomain_count = domain.count(".")
    if subdomain_count > 3:
        warnings.append(f"Excessive subdomains ({subdomain_count} levels)")

    # Check for IP-based URL
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        warnings.append("URL uses IP address instead of domain name")

    # Check for data URI or javascript
    if url.lower().startswith(("data:", "javascript:")):
        warnings.append("Dangerous URL scheme detected")

    # Check for very long URLs (common in phishing)
    if len(url) > 500:
        warnings.append("Unusually long URL")

    return warnings


def detect_phishing(url: str, check_type: str = "both") -> dict:
    """Run comprehensive phishing and dApp security detection."""
    url = validate_url(url)

    result: dict = {
        "success": True,
        "scan_type": "phishing_detection",
        "target_url": url,
        "domain": urllib.parse.urlparse(url).netloc,
    }

    # URL pattern analysis (always runs)
    pattern_warnings = analyze_url_patterns(url)
    result["url_pattern_analysis"] = {
        "warnings": pattern_warnings if pattern_warnings else None,
        "suspicious_patterns_found": len(pattern_warnings),
    }

    # GoPlus phishing check
    if check_type in ("phishing", "both"):
        phishing_result = check_phishing(url)
        result["phishing_check"] = {
            "is_phishing": phishing_result["is_phishing"],
            "source": "GoPlus Security Database",
        }

    # dApp security check
    if check_type in ("dapp", "both"):
        dapp_result = check_dapp_security(url)
        result["dapp_security"] = dapp_result

    # Calculate overall risk
    score = 0
    verdicts: list[str] = []

    if result.get("phishing_check", {}).get("is_phishing"):
        score += 5
        verdicts.append("CONFIRMED PHISHING SITE — do NOT connect wallet")

    if pattern_warnings:
        score += min(len(pattern_warnings), 3)
        verdicts.append(
            f"{len(pattern_warnings)} suspicious URL pattern(s) detected"
        )

    dapp = result.get("dapp_security", {})
    if dapp.get("available"):
        if dapp.get("is_trusted"):
            score = max(0, score - 2)
            verdicts.append("dApp is on GoPlus trusted list")
        if dapp.get("is_audited"):
            verdicts.append("dApp has been audited")
        malicious_contracts = [
            c for c in dapp.get("contracts", []) if c.get("malicious")
        ]
        if malicious_contracts:
            score += 4
            verdicts.append(
                f"{len(malicious_contracts)} malicious contract(s) associated"
            )

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

    result["risk_assessment"] = {
        "score": score,
        "level": level,
        "verdicts": verdicts,
    }

    return result


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        url = input_data.get("url", "")
        check_type = input_data.get("check_type", "both")

        if not url:
            print(
                json.dumps(
                    {
                        "error": "Provide 'url' parameter",
                        "example": {
                            "url": "https://app.uniswap.org",
                            "check_type": "both",
                        },
                    }
                )
            )
            sys.exit(1)

        if check_type not in ("phishing", "dapp", "both"):
            check_type = "both"

        result = detect_phishing(url, check_type)
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
