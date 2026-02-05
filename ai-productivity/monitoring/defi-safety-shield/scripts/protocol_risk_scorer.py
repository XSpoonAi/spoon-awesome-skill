#!/usr/bin/env python3
"""
Protocol Risk Scorer
Assesses DeFi protocol risk using TVL trends, audit status, chain diversity,
and metadata from the DeFi Llama API (free, no key required).

Author: Nihal Nihalani
Version: 1.0.0
"""

import json
import sys
import urllib.request
import urllib.error

DEFILLAMA_API = "https://api.llama.fi"


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
                "Rate limit exceeded. Please wait before retrying."
            )
        raise ConnectionError(f"API error (HTTP {e.code})")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Connection failed: {e.reason}")


def validate_protocol(protocol: str) -> str:
    """Validate and sanitize protocol name."""
    sanitized = protocol.strip().lower()
    if not sanitized:
        raise ValueError("Protocol name cannot be empty")
    if len(sanitized) > 100:
        raise ValueError("Protocol name too long")
    if not all(c.isalnum() or c in "-_. " for c in sanitized):
        raise ValueError("Protocol name contains invalid characters")
    return sanitized


def find_protocol(protocol_name: str) -> dict:
    """Find a protocol by name from the DeFi Llama protocols list."""
    url = f"{DEFILLAMA_API}/protocols"
    protocols = fetch_json(url)

    if not isinstance(protocols, list):
        raise ValueError("Failed to fetch protocols list")

    name_lower = protocol_name.lower()

    # Exact match on name or slug
    for p in protocols:
        if p.get("name", "").lower() == name_lower:
            return p
        if p.get("slug", "").lower() == name_lower:
            return p

    # Starts-with match (prefer highest TVL)
    starts_with = []
    for p in protocols:
        p_name = p.get("name", "").lower()
        p_slug = p.get("slug", "").lower()
        if p_name.startswith(name_lower) or p_slug.startswith(name_lower):
            starts_with.append(p)

    if starts_with:
        # Return the one with highest TVL
        starts_with.sort(key=lambda x: x.get("tvl", 0) or 0, reverse=True)
        return starts_with[0]

    # Partial/contains match
    matches = []
    for p in protocols:
        p_name = p.get("name", "").lower()
        p_slug = p.get("slug", "").lower()
        if name_lower in p_name or name_lower in p_slug:
            matches.append(p)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # Return highest TVL match
        matches.sort(key=lambda x: x.get("tvl", 0) or 0, reverse=True)
        return matches[0]
    else:
        raise ValueError(
            f"Protocol not found: {protocol_name}. "
            "Check the name on defillama.com."
        )


def calculate_protocol_risk(protocol: dict) -> dict:
    """Calculate risk score for a DeFi protocol."""
    score = 0
    factors: list[dict] = []

    tvl = protocol.get("tvl", 0) or 0
    change_1d = protocol.get("change_1d") or 0
    change_7d = protocol.get("change_7d") or 0
    chains = protocol.get("chains", [])
    category = protocol.get("category", "Unknown")
    audits = protocol.get("audits", "0")
    forked_from = protocol.get("forkedFrom", [])
    listed_at = protocol.get("listedAt", 0)

    # TVL size assessment
    if tvl < 100_000:
        score += 3
        factors.append({
            "factor": "Very low TVL",
            "detail": f"TVL is ${tvl:,.0f} — extremely low, high risk",
            "impact": "+3",
        })
    elif tvl < 1_000_000:
        score += 2
        factors.append({
            "factor": "Low TVL",
            "detail": f"TVL is ${tvl:,.0f} — below $1M threshold",
            "impact": "+2",
        })
    elif tvl < 10_000_000:
        score += 1
        factors.append({
            "factor": "Moderate TVL",
            "detail": f"TVL is ${tvl:,.0f}",
            "impact": "+1",
        })
    else:
        factors.append({
            "factor": "Strong TVL",
            "detail": f"TVL is ${tvl:,.0f}",
            "impact": "0 (positive signal)",
        })

    # TVL trend analysis
    if change_1d < -20:
        score += 3
        factors.append({
            "factor": "Severe TVL drop (24h)",
            "detail": f"TVL dropped {change_1d:.1f}% in 24h — potential bank run",
            "impact": "+3",
        })
    elif change_1d < -10:
        score += 2
        factors.append({
            "factor": "Major TVL decline (24h)",
            "detail": f"TVL dropped {change_1d:.1f}% in 24h",
            "impact": "+2",
        })
    elif change_1d < -5:
        score += 1
        factors.append({
            "factor": "Notable TVL decrease (24h)",
            "detail": f"TVL changed {change_1d:.1f}% in 24h",
            "impact": "+1",
        })

    if change_7d < -30:
        score += 2
        factors.append({
            "factor": "Severe TVL drop (7d)",
            "detail": f"TVL dropped {change_7d:.1f}% over 7 days",
            "impact": "+2",
        })
    elif change_7d < -15:
        score += 1
        factors.append({
            "factor": "TVL decline (7d)",
            "detail": f"TVL changed {change_7d:.1f}% over 7 days",
            "impact": "+1",
        })

    # Audit status
    if audits == "0" or not audits:
        score += 2
        factors.append({
            "factor": "No audits",
            "detail": "Protocol has no recorded security audits",
            "impact": "+2",
        })
    else:
        factors.append({
            "factor": "Audited",
            "detail": f"Audit status: {audits}",
            "impact": "0 (positive signal)",
        })

    # Chain diversity
    if len(chains) == 1:
        score += 1
        factors.append({
            "factor": "Single-chain deployment",
            "detail": f"Only deployed on {chains[0]}",
            "impact": "+1",
        })
    elif len(chains) >= 5:
        factors.append({
            "factor": "Multi-chain presence",
            "detail": f"Deployed on {len(chains)} chains",
            "impact": "0 (positive signal)",
        })

    # Fork status
    if forked_from and len(forked_from) > 0:
        score += 1
        factors.append({
            "factor": "Forked protocol",
            "detail": f"Forked from: {', '.join(forked_from[:3])}",
            "impact": "+1 (forked code may have undiscovered issues)",
        })

    # Protocol age
    if listed_at:
        import time

        age_days = (time.time() - listed_at) / 86400
        if age_days < 30:
            score += 2
            factors.append({
                "factor": "Very new protocol",
                "detail": f"Listed {int(age_days)} days ago",
                "impact": "+2",
            })
        elif age_days < 90:
            score += 1
            factors.append({
                "factor": "New protocol",
                "detail": f"Listed {int(age_days)} days ago",
                "impact": "+1",
            })
        elif age_days > 365:
            factors.append({
                "factor": "Established protocol",
                "detail": f"Operating for {int(age_days / 365)} year(s)",
                "impact": "0 (positive signal)",
            })

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
        "factors": factors,
    }


def score_protocol(protocol_name: str) -> dict:
    """Run comprehensive protocol risk assessment."""
    protocol_name = validate_protocol(protocol_name)
    protocol = find_protocol(protocol_name)

    risk = calculate_protocol_risk(protocol)

    # Build chain TVL breakdown
    chain_tvls = {}
    raw_chain_tvls = protocol.get("chainTvls", {})
    for chain, tvl_val in raw_chain_tvls.items():
        # Skip borrowed/staking sub-entries
        if "-" in chain:
            continue
        if isinstance(tvl_val, (int, float)):
            chain_tvls[chain] = round(tvl_val, 2)

    return {
        "success": True,
        "scan_type": "protocol_risk",
        "protocol": {
            "name": protocol.get("name", protocol_name),
            "slug": protocol.get("slug", protocol_name),
            "symbol": protocol.get("symbol", "N/A"),
            "category": protocol.get("category", "Unknown"),
            "url": protocol.get("url", "N/A"),
            "description": (protocol.get("description", "") or "")[:300],
        },
        "tvl": {
            "current_usd": round(protocol.get("tvl", 0) or 0, 2),
            "change_1d_percent": round(protocol.get("change_1d", 0) or 0, 2),
            "change_7d_percent": round(protocol.get("change_7d", 0) or 0, 2),
            "chain_breakdown": chain_tvls,
        },
        "metadata": {
            "chains": protocol.get("chains", []),
            "chain_count": len(protocol.get("chains", [])),
            "audits": protocol.get("audits", "0"),
            "forked_from": protocol.get("forkedFrom", []),
            "oracles": protocol.get("oracles", []),
            "twitter": protocol.get("twitter", "N/A"),
        },
        "risk_assessment": risk,
    }


def main() -> None:
    """Main entry point. Reads JSON from stdin."""
    try:
        input_data = json.loads(sys.stdin.read())

        protocol = input_data.get("protocol", "")

        if not protocol:
            print(
                json.dumps(
                    {
                        "error": "Provide 'protocol' parameter",
                        "example": {"protocol": "aave"},
                    }
                )
            )
            sys.exit(1)

        result = score_protocol(protocol)
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
