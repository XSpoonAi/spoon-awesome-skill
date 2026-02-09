#!/usr/bin/env python3
"""
EVM Transaction Error Classifier
Classifies and explains transaction failures, decodes revert reasons,
and provides human-readable explanations with suggested fixes.

Input (JSON via stdin):
{
    "tx_hash": "0x...",
    "chain": "ethereum"
}

Output (JSON via stdout):
{
    "success": true,
    "scan_type": "error_classification",
    "transaction": { ... },
    "error": { ... },
    "explanation": { ... },
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
    "ethereum": "1", "eth": "1",
    "bsc": "56", "bnb": "56",
    "polygon": "137", "matic": "137",
    "arbitrum": "42161", "arb": "42161",
    "base": "8453",
    "optimism": "10", "op": "10",
    "avalanche": "43114", "avax": "43114",
}

FOURBYTE_API: str = "https://www.4byte.directory/api/v1"

TX_HASH_PATTERN: re.Pattern = re.compile(r"^0x[a-fA-F0-9]{64}$")

MAX_RETRIES: int = 3
RETRY_BACKOFF: float = 1.0


# ---------------------------------------------------------------------------
# Error Taxonomy
# ---------------------------------------------------------------------------

ERROR_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "OUT_OF_GAS": {
        "description": "Transaction ran out of gas during execution.",
        "severity": "MEDIUM",
        "common_causes": [
            "Gas limit set too low for the operation",
            "Infinite loop or extremely complex computation in contract",
            "Contract storage operations more expensive than estimated",
            "Nested contract calls consuming more gas than expected",
        ],
        "suggested_fixes": [
            "Increase gas limit by 20-50% and retry",
            "Use gas estimation (eth_estimateGas) before submitting",
            "Check if the contract has changed since your last interaction",
            "Verify the transaction parameters are correct",
        ],
    },
    "REVERT": {
        "description": "Contract execution was explicitly reverted via require/revert/assert.",
        "severity": "LOW",
        "common_causes": [
            "Failed require() condition in the contract",
            "Explicit revert() call with reason string",
            "assert() failure (usually indicates a bug)",
            "Custom error thrown by the contract",
        ],
        "suggested_fixes": [
            "Read the revert reason for specific guidance",
            "Check your input parameters match contract expectations",
            "Verify you have sufficient token balance/allowance",
            "Check if the contract is paused or has time restrictions",
        ],
    },
    "INSUFFICIENT_FUNDS": {
        "description": "Sender account does not have enough native currency to cover value + gas.",
        "severity": "LOW",
        "common_causes": [
            "Account balance too low for the transaction value",
            "Insufficient balance to cover gas cost",
            "Previous pending transaction consumed expected funds",
        ],
        "suggested_fixes": [
            "Add more funds to the sending account",
            "Reduce the transaction value",
            "Wait for pending transactions to confirm first",
            "Check token balance if interacting with a token contract",
        ],
    },
    "NONCE_TOO_LOW": {
        "description": "Transaction nonce has already been used by a confirmed transaction.",
        "severity": "LOW",
        "common_causes": [
            "Transaction was already submitted and confirmed",
            "Another transaction with the same nonce was confirmed first",
            "Wallet nonce tracking is out of sync",
        ],
        "suggested_fixes": [
            "Refresh wallet/provider to get updated nonce",
            "Use the next available nonce",
            "Check if a previous transaction already completed the same action",
        ],
    },
    "CONTRACT_CREATION_FAILED": {
        "description": "Contract deployment transaction failed.",
        "severity": "HIGH",
        "common_causes": [
            "Constructor function reverted",
            "Insufficient gas for contract deployment",
            "Contract code exceeds maximum size (24KB EIP-170)",
            "Constructor arguments are invalid",
        ],
        "suggested_fixes": [
            "Check constructor arguments for validity",
            "Increase gas limit for deployment (deployments are gas-heavy)",
            "Verify contract code compiles correctly",
            "Check if contract size exceeds the 24KB limit",
        ],
    },
    "INVALID_OPCODE": {
        "description": "EVM encountered an invalid instruction during execution.",
        "severity": "HIGH",
        "common_causes": [
            "assert() failure in Solidity (consumes all gas)",
            "Jump to invalid position in bytecode",
            "Compiler bug producing invalid opcodes",
            "Self-destructed contract being called",
        ],
        "suggested_fixes": [
            "This usually indicates a contract bug -- contact the contract developers",
            "Verify you are interacting with the correct contract address",
            "Check if the contract has been self-destructed",
            "Try interacting with a different version of the contract",
        ],
    },
    "STACK_OVERFLOW": {
        "description": "EVM stack depth limit (1024) was exceeded.",
        "severity": "HIGH",
        "common_causes": [
            "Deeply nested contract calls exceeding 1024 depth",
            "Recursive contract calls without proper termination",
            "Complex multi-hop interactions (e.g., flash loan chains)",
        ],
        "suggested_fixes": [
            "Reduce the number of nested contract calls",
            "Break complex operations into multiple transactions",
            "Use a different execution path with fewer intermediate calls",
        ],
    },
    "UNKNOWN": {
        "description": "Transaction failed with an unrecognized error type.",
        "severity": "MEDIUM",
        "common_causes": [
            "Network-specific error not in standard taxonomy",
            "RPC node returned non-standard error",
            "Transaction was dropped or replaced",
        ],
        "suggested_fixes": [
            "Check the raw transaction receipt for more details",
            "Try submitting the transaction again",
            "Use a different RPC endpoint for more detailed error info",
        ],
    },
}


# Known revert reason selectors
REVERT_SELECTORS: Dict[str, str] = {
    "0x08c379a0": "Error(string)",
    "0x4e487b71": "Panic(uint256)",
}

# Solidity Panic codes (0x4e487b71)
PANIC_CODES: Dict[int, str] = {
    0x00: "Generic compiler panic",
    0x01: "assert() condition failed",
    0x11: "Arithmetic overflow or underflow",
    0x12: "Division or modulo by zero",
    0x21: "Conversion to invalid enum value",
    0x22: "Access to incorrectly encoded storage byte array",
    0x31: "pop() on empty array",
    0x32: "Array index out of bounds",
    0x41: "Allocation of too much memory",
    0x51: "Call to zero-initialized internal function",
}

# Common revert reason patterns and their explanations
REVERT_PATTERNS: List[Dict[str, str]] = [
    {
        "pattern": r"(?i)insufficient.*(output|amount|balance|liquidity)",
        "explanation": "The output amount or balance was less than the minimum required.",
        "fix": "Increase slippage tolerance or check token balances.",
    },
    {
        "pattern": r"(?i)expired|deadline",
        "explanation": "The transaction deadline has passed.",
        "fix": "Increase the deadline parameter or submit the transaction faster.",
    },
    {
        "pattern": r"(?i)transfer.*amount.*exceeds|exceeds.*balance",
        "explanation": "Attempting to transfer more tokens than the balance.",
        "fix": "Check token balance and reduce the transfer amount.",
    },
    {
        "pattern": r"(?i)not.*owner|only.*owner|ownable|unauthorized|access",
        "explanation": "The caller does not have the required permissions.",
        "fix": "Call the function from the authorized account (contract owner).",
    },
    {
        "pattern": r"(?i)paused|not.*active|disabled",
        "explanation": "The contract or function is currently paused/disabled.",
        "fix": "Wait for the contract to be unpaused or check the project's announcements.",
    },
    {
        "pattern": r"(?i)already.*initialized|initializ",
        "explanation": "The contract has already been initialized.",
        "fix": "This is a one-time operation; the contract is already set up.",
    },
    {
        "pattern": r"(?i)reentrancy|reentrant",
        "explanation": "Reentrancy guard prevented recursive execution.",
        "fix": "Ensure external calls are not triggering recursive contract calls.",
    },
    {
        "pattern": r"(?i)max.*supply|sold.*out|exceed.*max|max.*mint",
        "explanation": "Maximum supply or minting limit has been reached.",
        "fix": "The collection/token has reached its maximum supply. No more can be minted.",
    },
    {
        "pattern": r"(?i)slippage|price.*impact|too.*much",
        "explanation": "Price impact or slippage exceeds the allowed threshold.",
        "fix": "Increase slippage tolerance, reduce trade size, or try a different DEX.",
    },
    {
        "pattern": r"(?i)allowance|approve|permit",
        "explanation": "Token allowance is insufficient for the requested operation.",
        "fix": "Approve the contract to spend your tokens before calling this function.",
    },
    {
        "pattern": r"(?i)blacklist|blocked|banned|restricted",
        "explanation": "The address is blacklisted or restricted from this operation.",
        "fix": "The token/contract has restricted your address. Contact the project team.",
    },
    {
        "pattern": r"(?i)locked|lock|vesting|cliff",
        "explanation": "Tokens are locked or in a vesting period.",
        "fix": "Wait until the lock/vesting period expires before attempting withdrawal.",
    },
]


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


# ---------------------------------------------------------------------------
# Revert reason decoding
# ---------------------------------------------------------------------------

def _decode_revert_hex(hex_data: str) -> Tuple[str, str]:
    """Decode a hex-encoded revert reason.

    Returns:
        Tuple of (error_type, decoded_message).
    """
    if not hex_data or hex_data == "0x":
        return "EMPTY", ""

    data = hex_data
    if data.startswith("0x"):
        data = data[2:]

    # Error(string) selector: 08c379a0
    if data.startswith("08c379a0") and len(data) >= 136:
        try:
            # Skip selector (8 chars) + offset (64 chars) + length (64 chars)
            str_len = int(data[72:136], 16)
            str_hex = data[136:136 + str_len * 2]
            decoded = bytes.fromhex(str_hex).decode("utf-8", errors="replace").rstrip("\x00")
            return "Error(string)", decoded
        except (ValueError, IndexError):
            pass

    # Panic(uint256) selector: 4e487b71
    if data.startswith("4e487b71") and len(data) >= 72:
        try:
            panic_code = int(data[8:72], 16)
            description = PANIC_CODES.get(panic_code, f"Unknown panic code: {panic_code}")
            return "Panic(uint256)", f"Panic code {hex(panic_code)}: {description}"
        except (ValueError, IndexError):
            pass

    # Custom error -- try to decode selector via 4byte.directory
    if len(data) >= 8:
        selector = f"0x{data[:8]}"
        return "CUSTOM_ERROR", selector

    return "UNKNOWN_FORMAT", hex_data


def _lookup_custom_error(selector: str) -> Optional[str]:
    """Look up a custom error selector via 4byte.directory."""
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


def _match_revert_pattern(reason: str) -> Optional[Dict[str, str]]:
    """Match decoded revert reason against known patterns."""
    for pattern_info in REVERT_PATTERNS:
        if re.search(pattern_info["pattern"], reason):
            return {
                "explanation": pattern_info["explanation"],
                "fix": pattern_info["fix"],
            }
    return None


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------

def _classify_error(tx_data: Dict) -> Dict[str, Any]:
    """Classify the transaction error based on available data.

    Args:
        tx_data: Raw transaction data from Blockscout.

    Returns:
        Error classification dictionary.
    """
    status = tx_data.get("status", "")
    result = tx_data.get("result", "")
    revert_raw = tx_data.get("revert_reason")
    gas_used = int(tx_data.get("gas_used", 0))
    gas_limit = int(tx_data.get("gas_limit", tx_data.get("gas", 0)))

    # Check if transaction actually succeeded
    if status == "ok" or result == "success":
        return {
            "classification": "SUCCESS",
            "raw_revert_reason": None,
            "decoded_reason": "Transaction executed successfully.",
            "error_selector": None,
            "error_type": None,
        }

    # Attempt to decode the revert reason
    decoded_type = "UNKNOWN_FORMAT"
    decoded_msg = ""
    error_selector = None

    if revert_raw:
        raw_str = str(revert_raw)
        # Blockscout may return the decoded string directly
        if not raw_str.startswith("0x"):
            decoded_type = "Error(string)"
            decoded_msg = raw_str
        else:
            decoded_type, decoded_msg = _decode_revert_hex(raw_str)

    # Handle custom error lookup
    if decoded_type == "CUSTOM_ERROR" and decoded_msg.startswith("0x"):
        error_selector = decoded_msg
        custom_sig = _lookup_custom_error(error_selector)
        if custom_sig:
            decoded_msg = custom_sig
            decoded_type = f"CustomError: {custom_sig}"
        else:
            decoded_msg = f"Unknown custom error: {error_selector}"

    # Classify the error
    classification = "UNKNOWN"

    # Out-of-gas: gas_used == gas_limit (consumed all available gas)
    if gas_limit > 0 and gas_used >= gas_limit * 0.99:
        classification = "OUT_OF_GAS"
    elif decoded_type.startswith("Panic"):
        classification = "INVALID_OPCODE"
    elif decoded_type in ("Error(string)", "CustomError") or decoded_msg:
        classification = "REVERT"
    elif status == "error" and not revert_raw:
        # No revert reason + error status
        if gas_limit > 0 and gas_used >= gas_limit * 0.95:
            classification = "OUT_OF_GAS"
        else:
            classification = "REVERT"

    # Check for contract creation failure
    to_info = tx_data.get("to")
    is_creation = to_info is None or (isinstance(to_info, dict) and not to_info.get("hash"))
    if is_creation and classification in ("REVERT", "OUT_OF_GAS"):
        classification = "CONTRACT_CREATION_FAILED"

    return {
        "classification": classification,
        "raw_revert_reason": str(revert_raw) if revert_raw else None,
        "decoded_reason": decoded_msg or "No revert reason available",
        "error_selector": error_selector,
        "error_type": decoded_type if decoded_type != "UNKNOWN_FORMAT" else None,
    }


def _build_explanation(error_info: Dict, tx_data: Dict) -> Dict[str, Any]:
    """Build a human-readable explanation with suggested fixes."""
    classification = error_info["classification"]
    decoded_reason = error_info.get("decoded_reason", "")

    if classification == "SUCCESS":
        return {
            "summary": "This transaction completed successfully. No errors to classify.",
            "common_causes": [],
            "suggested_fixes": [],
        }

    taxonomy = ERROR_TAXONOMY.get(classification, ERROR_TAXONOMY["UNKNOWN"])

    summary = taxonomy["description"]
    causes = list(taxonomy["common_causes"])
    fixes = list(taxonomy["suggested_fixes"])

    # Enhance with pattern matching on the decoded reason
    if decoded_reason:
        match = _match_revert_pattern(decoded_reason)
        if match:
            summary = f"{taxonomy['description']} Revert reason: \"{decoded_reason}\". {match['explanation']}"
            fixes.insert(0, match["fix"])
        elif classification == "REVERT":
            summary = f"Contract reverted with: \"{decoded_reason}\""

    return {
        "summary": summary,
        "common_causes": causes,
        "suggested_fixes": fixes,
    }


def _compute_risk_score(error_info: Dict) -> Dict[str, Any]:
    """Compute a risk score for the error."""
    classification = error_info["classification"]
    severity_map = {
        "SUCCESS": (0, "SAFE"),
        "INSUFFICIENT_FUNDS": (1, "SAFE"),
        "NONCE_TOO_LOW": (1, "SAFE"),
        "REVERT": (3, "LOW"),
        "OUT_OF_GAS": (4, "MEDIUM"),
        "CONTRACT_CREATION_FAILED": (6, "HIGH"),
        "INVALID_OPCODE": (7, "HIGH"),
        "STACK_OVERFLOW": (7, "HIGH"),
        "UNKNOWN": (5, "MEDIUM"),
    }
    score, level = severity_map.get(classification, (5, "MEDIUM"))
    return {"score": score, "level": level}


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def classify_error(tx_hash: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Classify and explain a transaction error.

    Args:
        tx_hash: Transaction hash (0x + 64 hex).
        chain: Blockchain network name.

    Returns:
        Dictionary with error classification, explanation, and fixes.
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

    # Extract basic info
    status = tx_data.get("status", "unknown")
    is_success = status == "ok" or tx_data.get("result") == "success"
    block_number = tx_data.get("block", tx_data.get("block_number"))
    timestamp = tx_data.get("timestamp")

    from_info = tx_data.get("from", {}) or {}
    to_info = tx_data.get("to", {}) or {}
    from_addr = from_info.get("hash", "") if isinstance(from_info, dict) else str(from_info)
    to_addr = to_info.get("hash", "") if isinstance(to_info, dict) else str(to_info)

    # Classify
    error_info = _classify_error(tx_data)
    explanation = _build_explanation(error_info, tx_data)
    risk = _compute_risk_score(error_info)

    # Gas context
    gas_used = tx_data.get("gas_used", "0")
    gas_limit = tx_data.get("gas_limit", tx_data.get("gas", "0"))

    return {
        "success": True,
        "scan_type": "error_classification",
        "transaction": {
            "hash": tx_hash,
            "chain": chain,
            "chain_id": chain_id,
            "block_number": block_number,
            "timestamp": timestamp,
            "status": status,
            "is_success": is_success,
            "from_address": from_addr,
            "to_address": to_addr,
        },
        "error": error_info,
        "explanation": explanation,
        "gas_context": {
            "gas_used": str(gas_used),
            "gas_limit": str(gas_limit),
            "gas_exhausted": (
                int(gas_used) >= int(gas_limit) * 0.99
                if gas_limit and int(gas_limit) > 0
                else False
            ),
        },
        "risk_assessment": risk,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point: read JSON from stdin, classify error, write JSON to stdout."""
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

        result = classify_error(tx_hash, chain)
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
