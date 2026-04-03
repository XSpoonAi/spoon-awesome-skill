#!/usr/bin/env python3
"""
EVM Transaction Event Parser
Parses and decodes transaction event logs into human-readable descriptions
using Blockscout and 4byte.directory APIs.

Input (JSON via stdin):
{
    "tx_hash": "0x...",
    "chain": "ethereum"
}

Output (JSON via stdout):
{
    "success": true,
    "scan_type": "event_parse",
    "transaction": { ... },
    "events": { ... },
    "parsed_events": [ ... ],
    "event_summary": [ ... ]
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

FOURBYTE_EVENT_API: str = "https://www.4byte.directory/api/v1/event-signatures"

TX_HASH_PATTERN: re.Pattern = re.compile(r"^0x[a-fA-F0-9]{64}$")

MAX_RETRIES: int = 3
RETRY_BACKOFF: float = 1.0


# ---------------------------------------------------------------------------
# Well-known event topic0 hashes
# ---------------------------------------------------------------------------

KNOWN_EVENTS: Dict[str, Dict[str, Any]] = {
    # ERC-20 / ERC-721
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef": {
        "name": "Transfer",
        "signature": "Transfer(address,address,uint256)",
        "params": ["from", "to", "value"],
        "param_types": ["address", "address", "uint256"],
        "category": "token_transfer",
    },
    "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925": {
        "name": "Approval",
        "signature": "Approval(address,address,uint256)",
        "params": ["owner", "spender", "value"],
        "param_types": ["address", "address", "uint256"],
        "category": "approval",
    },
    # ERC-1155
    "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62": {
        "name": "TransferSingle",
        "signature": "TransferSingle(address,address,address,uint256,uint256)",
        "params": ["operator", "from", "to", "id", "value"],
        "param_types": ["address", "address", "address", "uint256", "uint256"],
        "category": "token_transfer",
    },
    "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb": {
        "name": "TransferBatch",
        "signature": "TransferBatch(address,address,address,uint256[],uint256[])",
        "params": ["operator", "from", "to", "ids", "values"],
        "param_types": ["address", "address", "address", "uint256[]", "uint256[]"],
        "category": "token_transfer",
    },
    # Uniswap V2
    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822": {
        "name": "Swap",
        "signature": "Swap(address,uint256,uint256,uint256,uint256,address)",
        "params": ["sender", "amount0In", "amount1In", "amount0Out", "amount1Out", "to"],
        "param_types": ["address", "uint256", "uint256", "uint256", "uint256", "address"],
        "category": "dex_swap",
    },
    "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1": {
        "name": "Sync",
        "signature": "Sync(uint112,uint112)",
        "params": ["reserve0", "reserve1"],
        "param_types": ["uint112", "uint112"],
        "category": "dex_sync",
    },
    "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f": {
        "name": "Mint",
        "signature": "Mint(address,uint256,uint256)",
        "params": ["sender", "amount0", "amount1"],
        "param_types": ["address", "uint256", "uint256"],
        "category": "liquidity",
    },
    "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496": {
        "name": "Burn",
        "signature": "Burn(address,uint256,uint256,address)",
        "params": ["sender", "amount0", "amount1", "to"],
        "param_types": ["address", "uint256", "uint256", "address"],
        "category": "liquidity",
    },
    # Uniswap V3
    "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67": {
        "name": "Swap",
        "signature": "Swap(address,address,int256,int256,uint160,uint128,int24)",
        "params": ["sender", "recipient", "amount0", "amount1", "sqrtPriceX96", "liquidity", "tick"],
        "param_types": ["address", "address", "int256", "int256", "uint160", "uint128", "int24"],
        "category": "dex_swap_v3",
    },
    # WETH
    "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c": {
        "name": "Deposit",
        "signature": "Deposit(address,uint256)",
        "params": ["dst", "wad"],
        "param_types": ["address", "uint256"],
        "category": "wrap",
    },
    "0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65": {
        "name": "Withdrawal",
        "signature": "Withdrawal(address,uint256)",
        "params": ["src", "wad"],
        "param_types": ["address", "uint256"],
        "category": "unwrap",
    },
    # Ownership
    "0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0": {
        "name": "OwnershipTransferred",
        "signature": "OwnershipTransferred(address,address)",
        "params": ["previousOwner", "newOwner"],
        "param_types": ["address", "address"],
        "category": "governance",
    },
    # ERC-20 common
    "0x62e78cea01bee320cd4e420270b5ea74000d11b0c9f74754ebdbfc544b05a258": {
        "name": "Paused",
        "signature": "Paused(address)",
        "params": ["account"],
        "param_types": ["address"],
        "category": "admin",
    },
    "0x5db9ee0a495bf2e6ff9c91a7834c1ba4fdd244a5e8aa4e537bd38aeae4b073aa": {
        "name": "Unpaused",
        "signature": "Unpaused(address)",
        "params": ["account"],
        "param_types": ["address"],
        "category": "admin",
    },
}


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


def _shorten_address(address: str) -> str:
    """Shorten an address to 0xAbCd...EfGh format."""
    if not address or len(address) < 10:
        return address or "0x0"
    return f"{address[:6]}...{address[-4:]}"


def _topic_to_address(topic: str) -> str:
    """Extract address from a 32-byte topic (right-padded)."""
    if not topic:
        return "0x0"
    # Remove 0x prefix and leading zeros, then re-add 0x
    hex_val = topic.replace("0x", "").lstrip("0")
    if len(hex_val) < 40:
        hex_val = hex_val.zfill(40)
    return f"0x{hex_val[-40:]}"


def _topic_to_uint256(topic: str) -> str:
    """Extract uint256 value from a 32-byte topic."""
    if not topic:
        return "0"
    try:
        return str(int(topic, 16))
    except (ValueError, TypeError):
        return "0"


def _decode_data_word(data: str, offset: int) -> str:
    """Extract a 32-byte word from log data at the given word offset."""
    start = offset * 64
    end = start + 64
    if len(data) < end:
        return "0" * 64
    return data[start:end]


def _data_word_to_uint256(word: str) -> str:
    """Convert a 32-byte hex word to uint256 string."""
    try:
        return str(int(word, 16))
    except (ValueError, TypeError):
        return "0"


def _data_word_to_address(word: str) -> str:
    """Convert a 32-byte hex word to address."""
    return f"0x{word[-40:]}" if len(word) >= 40 else f"0x{word}"


# ---------------------------------------------------------------------------
# Event lookup
# ---------------------------------------------------------------------------

def _lookup_event_4byte(topic0: str) -> Optional[str]:
    """Look up an event signature via 4byte.directory.

    Args:
        topic0: The topic0 hash (with 0x prefix).

    Returns:
        Event text signature if found, else None.
    """
    url = f"{FOURBYTE_EVENT_API}/?hex_signature={topic0}&format=json"
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
# Event decoding
# ---------------------------------------------------------------------------

def _decode_known_event(
    event_info: Dict[str, Any],
    topics: List[str],
    data: str,
) -> Dict[str, Any]:
    """Decode a known event using the event definition.

    Args:
        event_info: Event definition from KNOWN_EVENTS.
        topics: List of topic hex strings.
        data: Hex data string (without 0x prefix).

    Returns:
        Dictionary of decoded parameter name-value pairs.
    """
    params = event_info.get("params", [])
    param_types = event_info.get("param_types", [])
    decoded: Dict[str, str] = {}

    # indexed params come from topics (starting at topics[1])
    # non-indexed params come from data
    topic_idx = 1  # topics[0] is the event signature
    data_idx = 0

    for i, (name, ptype) in enumerate(zip(params, param_types)):
        # For known events, assume standard indexed layout:
        # addresses and uint256 are typically indexed, arrays/complex types are not
        if topic_idx < len(topics) and ptype in ("address", "uint256", "uint112", "uint128", "uint160", "int256", "int24"):
            topic = topics[topic_idx]
            if "address" in ptype:
                decoded[name] = _topic_to_address(topic)
            else:
                decoded[name] = _topic_to_uint256(topic)
            topic_idx += 1
        else:
            # Read from data
            word = _decode_data_word(data, data_idx)
            if "address" in ptype:
                decoded[name] = _data_word_to_address(word)
            else:
                decoded[name] = _data_word_to_uint256(word)
            data_idx += 1

    return decoded


def _build_event_description(event_name: str, decoded_params: Dict[str, str], contract_name: Optional[str]) -> str:
    """Build a human-readable description of the event.

    Args:
        event_name: Name of the event.
        decoded_params: Decoded parameter key-value pairs.
        contract_name: Optional contract name.

    Returns:
        Human-readable string.
    """
    contract_label = contract_name or "contract"

    if event_name == "Transfer":
        from_addr = _shorten_address(decoded_params.get("from", ""))
        to_addr = _shorten_address(decoded_params.get("to", ""))
        value = decoded_params.get("value", "0")
        return f"Transfer {value} units from {from_addr} to {to_addr} on {contract_label}"

    if event_name == "Approval":
        owner = _shorten_address(decoded_params.get("owner", ""))
        spender = _shorten_address(decoded_params.get("spender", ""))
        value = decoded_params.get("value", "0")
        # Check for unlimited approval
        try:
            val_int = int(value)
            if val_int > 2**200:
                value = "unlimited"
        except (ValueError, TypeError):
            pass
        return f"{owner} approved {spender} to spend {value} on {contract_label}"

    if event_name == "Swap" and "amount0In" in decoded_params:
        # Uniswap V2 style
        sender = _shorten_address(decoded_params.get("sender", ""))
        to = _shorten_address(decoded_params.get("to", ""))
        a0in = decoded_params.get("amount0In", "0")
        a1in = decoded_params.get("amount1In", "0")
        a0out = decoded_params.get("amount0Out", "0")
        a1out = decoded_params.get("amount1Out", "0")
        return f"Swap on {contract_label}: {a0in}/{a1in} in -> {a0out}/{a1out} out (sender={sender}, to={to})"

    if event_name == "Swap" and "amount0" in decoded_params:
        # Uniswap V3 style
        sender = _shorten_address(decoded_params.get("sender", ""))
        recipient = _shorten_address(decoded_params.get("recipient", ""))
        a0 = decoded_params.get("amount0", "0")
        a1 = decoded_params.get("amount1", "0")
        return f"V3 Swap on {contract_label}: amount0={a0}, amount1={a1} (sender={sender}, to={recipient})"

    if event_name == "Deposit":
        dst = _shorten_address(decoded_params.get("dst", ""))
        wad = decoded_params.get("wad", "0")
        return f"Deposited {wad} wei to {contract_label} by {dst}"

    if event_name == "Withdrawal":
        src = _shorten_address(decoded_params.get("src", ""))
        wad = decoded_params.get("wad", "0")
        return f"Withdrew {wad} wei from {contract_label} by {src}"

    if event_name == "OwnershipTransferred":
        prev = _shorten_address(decoded_params.get("previousOwner", ""))
        new = _shorten_address(decoded_params.get("newOwner", ""))
        return f"Ownership of {contract_label} transferred from {prev} to {new}"

    if event_name == "TransferSingle":
        op = _shorten_address(decoded_params.get("operator", ""))
        from_addr = _shorten_address(decoded_params.get("from", ""))
        to_addr = _shorten_address(decoded_params.get("to", ""))
        token_id = decoded_params.get("id", "?")
        value = decoded_params.get("value", "0")
        return f"ERC-1155 transfer: {value} of token #{token_id} from {from_addr} to {to_addr} (operator={op})"

    if event_name == "Sync":
        r0 = decoded_params.get("reserve0", "0")
        r1 = decoded_params.get("reserve1", "0")
        return f"Pool reserves synced on {contract_label}: reserve0={r0}, reserve1={r1}"

    if event_name == "Paused":
        account = _shorten_address(decoded_params.get("account", ""))
        return f"{contract_label} paused by {account}"

    if event_name == "Unpaused":
        account = _shorten_address(decoded_params.get("account", ""))
        return f"{contract_label} unpaused by {account}"

    # Generic description
    param_strs = [f"{k}={v}" for k, v in decoded_params.items()]
    return f"{event_name} on {contract_label}: {', '.join(param_strs)}" if param_strs else f"{event_name} emitted by {contract_label}"


# ---------------------------------------------------------------------------
# Log parsing
# ---------------------------------------------------------------------------

def _parse_single_log(log_entry: Dict, index: int) -> Dict[str, Any]:
    """Parse a single log entry from Blockscout.

    Args:
        log_entry: Raw log data from Blockscout API.
        index: Log index in the transaction.

    Returns:
        Parsed event dictionary.
    """
    topics = log_entry.get("topics", [])
    raw_data = log_entry.get("data", "0x")
    data = raw_data.replace("0x", "") if raw_data else ""

    # Contract info
    address_info = log_entry.get("address", {})
    contract_address = ""
    contract_name = None
    if isinstance(address_info, dict):
        contract_address = address_info.get("hash", "")
        contract_name = address_info.get("name")
    elif isinstance(address_info, str):
        contract_address = address_info

    # Blockscout may provide decoded data directly
    decoded_bs = log_entry.get("decoded")

    topic0 = topics[0] if topics else None
    event_name = None
    event_signature = None
    decoded_params: Dict[str, str] = {}
    resolved = False
    category = "unknown"

    # Try known events first
    if topic0 and topic0.lower() in KNOWN_EVENTS:
        known = KNOWN_EVENTS[topic0.lower()]
        event_name = known["name"]
        event_signature = known["signature"]
        category = known.get("category", "unknown")
        decoded_params = _decode_known_event(known, topics, data)
        resolved = True

    # Use Blockscout decoded data if available
    elif decoded_bs and isinstance(decoded_bs, dict):
        event_name = decoded_bs.get("method_call", decoded_bs.get("method_id", ""))
        if "(" in event_name:
            event_signature = event_name
            event_name = event_name.split("(")[0]
        params = decoded_bs.get("parameters", [])
        if isinstance(params, list):
            for p in params:
                pname = p.get("name", f"param_{len(decoded_params)}")
                pval = str(p.get("value", ""))
                decoded_params[pname] = pval
        resolved = True

    # Fall back to 4byte.directory lookup
    elif topic0:
        sig = _lookup_event_4byte(topic0)
        if sig:
            event_name = sig.split("(")[0]
            event_signature = sig
            resolved = True

    if not event_name:
        event_name = f"Unknown({topic0[:10] if topic0 else '???'})"

    description = _build_event_description(
        event_name, decoded_params, contract_name
    )

    return {
        "index": index,
        "event_name": event_name,
        "signature": event_signature,
        "contract_address": contract_address,
        "contract_name": contract_name,
        "category": category,
        "topics": topics,
        "decoded_params": decoded_params if decoded_params else None,
        "raw_data": raw_data if not resolved else None,
        "resolved": resolved,
        "description": description,
    }


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def parse_events(tx_hash: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Parse transaction event logs.

    Args:
        tx_hash: Transaction hash (0x + 64 hex).
        chain: Blockchain network name.

    Returns:
        Dictionary with parsed events and summaries.
    """
    tx_hash = _validate_tx_hash(tx_hash)
    chain = _validate_chain(chain)
    chain_id = CHAIN_IDS.get(chain, "1")
    base_url = BLOCKSCOUT_CHAINS[chain]

    # Fetch transaction basic info
    tx_url = f"{base_url}/api/v2/transactions/{tx_hash}"
    tx_data = _fetch_json(tx_url)
    if not tx_data:
        raise ValueError(
            f"Transaction {tx_hash} not found on {chain}. "
            "Verify the hash and chain are correct."
        )

    status = tx_data.get("status", "unknown")
    is_success = status == "ok" or tx_data.get("result") == "success"

    # Fetch logs
    logs_url = f"{base_url}/api/v2/transactions/{tx_hash}/logs"
    logs_data = _fetch_json(logs_url)

    raw_logs: List[Dict] = []
    if logs_data:
        if isinstance(logs_data, dict):
            raw_logs = logs_data.get("items", [])
        elif isinstance(logs_data, list):
            raw_logs = logs_data

    # Parse each log
    parsed_events: List[Dict[str, Any]] = []
    decoded_count = 0
    unresolved_count = 0

    for idx, log_entry in enumerate(raw_logs):
        parsed = _parse_single_log(log_entry, idx)
        parsed_events.append(parsed)
        if parsed.get("resolved"):
            decoded_count += 1
        else:
            unresolved_count += 1

    # Build summary strings
    event_summary: List[str] = []
    for i, evt in enumerate(parsed_events):
        desc = evt.get("description", evt.get("event_name", "Unknown"))
        event_summary.append(f"{i + 1}. {desc}")

    # Category breakdown
    categories: Dict[str, int] = {}
    for evt in parsed_events:
        cat = evt.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "success": True,
        "scan_type": "event_parse",
        "transaction": {
            "hash": tx_hash,
            "chain": chain,
            "chain_id": chain_id,
            "block_number": tx_data.get("block", tx_data.get("block_number")),
            "timestamp": tx_data.get("timestamp"),
            "status": status,
            "is_success": is_success,
        },
        "events": {
            "total": len(parsed_events),
            "decoded": decoded_count,
            "unresolved": unresolved_count,
        },
        "categories": categories,
        "parsed_events": parsed_events,
        "event_summary": event_summary,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point: read JSON from stdin, parse events, write JSON to stdout."""
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

        result = parse_events(tx_hash, chain)
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
