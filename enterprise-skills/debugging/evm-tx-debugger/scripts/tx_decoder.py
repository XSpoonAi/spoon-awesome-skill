#!/usr/bin/env python3
"""
EVM Transaction Decoder
Decodes transaction input data, method calls, and parameters using
Blockscout and 4byte.directory APIs.

Input (JSON via stdin):
{
    "tx_hash": "0x...",
    "chain": "ethereum"
}

Output (JSON via stdout):
{
    "success": true,
    "scan_type": "transaction_decode",
    "transaction": { ... },
    "method": { ... },
    "gas": { ... },
    ...
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

FOURBYTE_API: str = "https://www.4byte.directory/api/v1"

TX_HASH_PATTERN: re.Pattern = re.compile(r"^0x[a-fA-F0-9]{64}$")

MAX_RETRIES: int = 3
RETRY_BACKOFF: float = 1.0


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
    # Map aliases to canonical names
    alias_to_canonical: Dict[str, str] = {
        "eth": "ethereum",
        "bnb": "bsc",
        "matic": "polygon",
        "arb": "arbitrum",
        "op": "optimism",
        "avax": "avalanche",
    }
    canonical = alias_to_canonical.get(chain_lower, chain_lower)
    if canonical not in BLOCKSCOUT_CHAINS:
        supported = ", ".join(sorted(BLOCKSCOUT_CHAINS.keys()))
        raise ValueError(
            f"Unsupported chain: {chain}. Supported chains: {supported}"
        )
    return canonical


def _wei_to_eth(wei_str: str) -> str:
    """Convert a wei string value to ETH as a decimal string."""
    try:
        wei = int(wei_str)
        return f"{wei / 1e18:.18f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return "0"


def _gwei(wei_str: str) -> float:
    """Convert wei string to Gwei float."""
    try:
        return int(wei_str) / 1e9
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def _fetch_tx_from_blockscout(tx_hash: str, chain: str) -> Optional[Dict]:
    """Fetch transaction details from Blockscout."""
    base_url = BLOCKSCOUT_CHAINS[chain]
    url = f"{base_url}/api/v2/transactions/{tx_hash}"
    return _fetch_json(url)


def _decode_selector_4byte(hex_selector: str) -> Optional[str]:
    """Resolve a 4-byte method selector via 4byte.directory."""
    if not hex_selector or len(hex_selector) < 10:
        return None
    selector = hex_selector[:10]  # 0x + 8 hex chars
    url = f"{FOURBYTE_API}/signatures/?hex_signature={selector}&format=json"
    try:
        data = _fetch_json(url, timeout=10, retries=2)
        if data and data.get("results"):
            results = data["results"]
            canonical = min(results, key=lambda r: r.get("id", 0))
            return canonical.get("text_signature")
    except ConnectionError:
        pass
    return None


# ---------------------------------------------------------------------------
# Known method selectors for common operations
# ---------------------------------------------------------------------------

KNOWN_SELECTORS: Dict[str, str] = {
    "0xa9059cbb": "transfer(address,uint256)",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0x095ea7b3": "approve(address,uint256)",
    "0x70a08231": "balanceOf(address)",
    "0x18160ddd": "totalSupply()",
    "0xdd62ed3e": "allowance(address,address)",
    "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
    "0x7ff36ab5": "swapExactETHForTokens(uint256,address[],address,uint256)",
    "0x18cbafe5": "swapExactTokensForETH(uint256,uint256,address[],address,uint256)",
    "0xfb3bdb41": "swapETHForExactTokens(uint256,address[],address,uint256)",
    "0x5c11d795": "swapExactTokensForTokensSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)",
    "0xb6f9de95": "swapExactETHForTokensSupportingFeeOnTransferTokens(uint256,address[],address,uint256)",
    "0x791ac947": "swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)",
    "0xe8e33700": "addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)",
    "0xf305d719": "addLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
    "0xbaa2abde": "removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)",
    "0x02751cec": "removeLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
    "0x3593564c": "execute(bytes,bytes[],uint256)",
    "0xac9650d8": "multicall(bytes[])",
    "0x5ae401dc": "multicall(uint256,bytes[])",
    "0x1249c58b": "mint()",
    "0xa0712d68": "mint(uint256)",
    "0x40c10f19": "mint(address,uint256)",
    "0x42842e0e": "safeTransferFrom(address,address,uint256)",
    "0xb88d4fde": "safeTransferFrom(address,address,uint256,bytes)",
    "0xd0e30db0": "deposit()",
    "0x2e1a7d4d": "withdraw(uint256)",
    "0x3659cfe6": "upgradeTo(address)",
    "0x4f1ef286": "upgradeToAndCall(address,bytes)",
    "0x715018a6": "renounceOwnership()",
    "0xf2fde38b": "transferOwnership(address)",
}


# ---------------------------------------------------------------------------
# Decode logic
# ---------------------------------------------------------------------------

def _extract_method_info(raw_input: str) -> Dict[str, Any]:
    """Extract method selector and attempt to decode it."""
    if not raw_input or raw_input == "0x" or len(raw_input) < 10:
        return {
            "selector": None,
            "name": None,
            "signature": None,
            "decoded_inputs": "Plain ETH/native transfer (no input data)",
            "is_plain_transfer": True,
        }

    selector = raw_input[:10].lower()

    # Try known selectors first
    signature = KNOWN_SELECTORS.get(selector)
    source = "known database"

    # Fall back to 4byte.directory
    if not signature:
        signature = _decode_selector_4byte(selector)
        source = "4byte.directory"

    if signature:
        name = signature.split("(")[0]
        decoded = f"{selector} -> {signature} (via {source})"
    else:
        name = None
        decoded = f"{selector} -> unknown method (selector not found)"

    # Extract raw parameter data
    param_data = raw_input[10:] if len(raw_input) > 10 else ""
    param_words: List[str] = []
    for i in range(0, len(param_data), 64):
        word = param_data[i:i + 64]
        if word:
            param_words.append(f"0x{word}")

    return {
        "selector": selector,
        "name": name,
        "signature": signature,
        "decoded_inputs": decoded,
        "is_plain_transfer": False,
        "raw_param_count": len(param_words),
        "raw_params": param_words[:10],  # Limit to first 10 words
    }


def _extract_contract_info(tx_data: Dict) -> Dict[str, Any]:
    """Extract contract interaction details from Blockscout tx data."""
    to_info = tx_data.get("to", {}) or {}
    is_contract = to_info.get("is_contract", False) if isinstance(to_info, dict) else False
    contract_name = None
    contract_verified = False

    if isinstance(to_info, dict):
        contract_name = to_info.get("name")
        contract_verified = to_info.get("is_verified", False)

    return {
        "is_contract_call": is_contract,
        "contract_name": contract_name,
        "contract_verified": contract_verified,
    }


def decode_transaction(tx_hash: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Decode a transaction's input data and context.

    Args:
        tx_hash: Transaction hash (0x + 64 hex).
        chain: Blockchain network name.

    Returns:
        Dictionary with decoded transaction information.
    """
    tx_hash = _validate_tx_hash(tx_hash)
    chain = _validate_chain(chain)
    chain_id = CHAIN_IDS.get(chain, "1")
    native = CHAIN_NATIVE_CURRENCY.get(chain, "ETH")

    # Fetch transaction from Blockscout
    tx_data = _fetch_tx_from_blockscout(tx_hash, chain)
    if not tx_data:
        raise ValueError(
            f"Transaction {tx_hash} not found on {chain}. "
            "Verify the hash and chain are correct."
        )

    # Extract basic fields
    status = tx_data.get("status", "unknown")
    is_success = status == "ok" or tx_data.get("result") == "success"
    block_number = tx_data.get("block", tx_data.get("block_number"))
    timestamp = tx_data.get("timestamp")

    # Addresses
    from_info = tx_data.get("from", {}) or {}
    to_info = tx_data.get("to", {}) or {}
    from_addr = from_info.get("hash", "") if isinstance(from_info, dict) else str(from_info)
    to_addr = to_info.get("hash", "") if isinstance(to_info, dict) else str(to_info)

    # Value
    value_wei = tx_data.get("value", "0")
    value_eth = _wei_to_eth(value_wei)

    # Decode method
    raw_input = tx_data.get("raw_input", tx_data.get("input", "0x"))
    method_info = _extract_method_info(raw_input or "0x")

    # Blockscout may provide decoded input
    decoded_input_bs = tx_data.get("decoded_input")
    if decoded_input_bs and isinstance(decoded_input_bs, dict):
        bs_method = decoded_input_bs.get("method_call")
        bs_name = decoded_input_bs.get("method_id")
        if bs_method and not method_info.get("signature"):
            method_info["signature"] = bs_method
            method_info["name"] = bs_method.split("(")[0] if "(" in bs_method else bs_method
            method_info["decoded_inputs"] = f"{method_info['selector']} -> {bs_method} (via Blockscout)"
        # Extract decoded parameters from Blockscout
        bs_params = decoded_input_bs.get("parameters")
        if bs_params and isinstance(bs_params, list):
            method_info["decoded_parameters"] = [
                {
                    "name": p.get("name", ""),
                    "type": p.get("type", ""),
                    "value": str(p.get("value", "")),
                }
                for p in bs_params[:20]
            ]

    # Gas
    gas_used = tx_data.get("gas_used", "0")
    gas_limit = tx_data.get("gas_limit", tx_data.get("gas", "0"))
    gas_price = tx_data.get("gas_price", "0")
    max_fee = tx_data.get("max_fee_per_gas")
    max_priority = tx_data.get("max_priority_fee_per_gas")

    gas_info: Dict[str, Any] = {
        "gas_used": str(gas_used),
        "gas_limit": str(gas_limit),
        "gas_price_gwei": _gwei(str(gas_price)),
    }
    if max_fee:
        gas_info["max_fee_per_gas_gwei"] = _gwei(str(max_fee))
    if max_priority:
        gas_info["max_priority_fee_per_gas_gwei"] = _gwei(str(max_priority))

    # Contract interaction info
    contract_info = _extract_contract_info(tx_data)

    # Transaction type
    tx_type = tx_data.get("tx_types", [])
    if isinstance(tx_type, list):
        tx_type_str = ", ".join(tx_type) if tx_type else "legacy"
    else:
        tx_type_str = str(tx_type)

    # Nonce
    nonce = tx_data.get("nonce")

    # Revert reason (if failed)
    revert_reason = tx_data.get("revert_reason")

    result: Dict[str, Any] = {
        "success": True,
        "scan_type": "transaction_decode",
        "transaction": {
            "hash": tx_hash,
            "chain": chain,
            "chain_id": chain_id,
            "block_number": block_number,
            "timestamp": timestamp,
            "status": status,
            "is_success": is_success,
            "type": tx_type_str,
            "nonce": nonce,
        },
        "from_address": from_addr,
        "to_address": to_addr,
        "value_wei": str(value_wei),
        "value_native": f"{value_eth} {native}",
        "method": method_info,
        "gas": gas_info,
        "contract_interaction": contract_info,
    }

    if revert_reason:
        result["revert_reason"] = revert_reason

    # Token transfers (if Blockscout provides them)
    token_transfers = tx_data.get("token_transfers")
    if token_transfers and isinstance(token_transfers, list):
        result["token_transfers"] = [
            {
                "token_name": t.get("token", {}).get("name", "Unknown"),
                "token_symbol": t.get("token", {}).get("symbol", "???"),
                "from": t.get("from", {}).get("hash", "") if isinstance(t.get("from"), dict) else "",
                "to": t.get("to", {}).get("hash", "") if isinstance(t.get("to"), dict) else "",
                "value": str(t.get("total", {}).get("value", t.get("value", "0"))),
                "token_type": t.get("token", {}).get("type", "ERC-20"),
            }
            for t in token_transfers[:20]
        ]

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point: read JSON from stdin, decode transaction, write JSON to stdout."""
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

        result = decode_transaction(tx_hash, chain)
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
