#!/usr/bin/env python3
"""EVM Proxy Upgrade Analyzer.

Detect common EVM proxy patterns (EIP-1967, Beacon, EIP-1167 minimal proxy) and
report implementation/admin/beacon addresses plus basic risk flags.

- Demo mode is fully offline (no RPC required).
- Non-demo mode uses JSON-RPC over HTTP.

Output is always JSON:
  - success: {"ok": true, "data": {...}}
  - error:   {"ok": false, "error": "...", "details": {...}}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple


EIP1967_IMPLEMENTATION_SLOT = (
    "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
)
EIP1967_ADMIN_SLOT = (
    "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
)
EIP1967_BEACON_SLOT = (
    "0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50"
)

SELECTOR_IMPLEMENTATION = "0x5c60da1b"  # implementation()
SELECTOR_PROXIABLE_UUID = "0x52d1902d"  # proxiableUUID()

ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _success(data: Dict[str, Any]) -> str:
    return _json_dumps({"ok": True, "data": data})


def _error(message: str, details: Optional[Dict[str, Any]] = None) -> str:
    payload: Dict[str, Any] = {"ok": False, "error": message}
    if details is not None:
        payload["details"] = details
    return _json_dumps(payload)


def _read_stdin_json() -> Optional[Dict[str, Any]]:
    if sys.stdin is None or sys.stdin.isatty():
        return None
    raw = sys.stdin.read().strip()
    if not raw:
        return None
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("stdin JSON must be an object")
    return parsed


def _normalize_address(addr: str) -> str:
    if not isinstance(addr, str):
        raise ValueError("address must be a string")
    a = addr.strip()
    if not ADDR_RE.match(a):
        raise ValueError(f"Invalid address: {addr}")
    return "0x" + a[2:].lower()


def _normalize_block(block: Any) -> str:
    if block is None:
        return "latest"
    if isinstance(block, int):
        if block < 0:
            raise ValueError("block must be >= 0")
        return hex(block)
    if isinstance(block, str):
        b = block.strip()
        if not b:
            return "latest"
        return b
    raise ValueError("block must be a string (e.g. 'latest' or '0x123') or an integer")


def _strip_0x(h: str) -> str:
    if not isinstance(h, str):
        return ""
    return h[2:] if h.startswith("0x") else h


def _hex_to_bytes32(h: str) -> bytes:
    s = _strip_0x(h).lower()
    if s == "":
        s = "0"
    if any(c not in "0123456789abcdef" for c in s):
        raise ValueError(f"Invalid hex: {h}")
    if len(s) > 64:
        # Some nodes return full words only; truncate left if oversized.
        s = s[-64:]
    s = s.rjust(64, "0")
    return bytes.fromhex(s)


def _bytes32_to_address(b32: bytes) -> Optional[str]:
    if len(b32) != 32:
        raise ValueError("expected 32 bytes")
    addr = b32[-20:]
    if addr == b"\x00" * 20:
        return None
    return "0x" + addr.hex()


def _parse_storage_address(storage_hex: str) -> Optional[str]:
    return _bytes32_to_address(_hex_to_bytes32(storage_hex))


def _parse_return_address(ret_hex: str) -> Optional[str]:
    if not isinstance(ret_hex, str) or ret_hex in ("0x", ""):
        return None
    b = _hex_to_bytes32(ret_hex)
    return _bytes32_to_address(b)


def _match_eip1167_minimal_proxy(code_hex: str) -> Optional[str]:
    """Return implementation address if code matches EIP-1167 minimal proxy runtime."""

    code = _strip_0x(code_hex).lower()
    # EIP-1167 minimal proxy runtime:
    # 363d3d373d3d3d363d73 <20-byte impl> 5af43d82803e903d91602b57fd5bf3
    m = re.fullmatch(
        r"363d3d373d3d3d363d73([0-9a-f]{40})5af43d82803e903d91602b57fd5bf3",
        code,
    )
    if not m:
        return None
    return "0x" + m.group(1)


class JsonRpcProvider:
    def __init__(self, rpc_url: str, *, timeout_seconds: int = 20, max_retries: int = 1):
        if not isinstance(rpc_url, str) or not rpc_url.strip():
            raise ValueError("rpc_url is required")
        self._url = rpc_url
        self._timeout = timeout_seconds
        self._max_retries = max_retries
        self._next_id = 1

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import requests  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "requests is required. Install with: pip install -r requirements.txt"
            ) from e

        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = requests.post(
                    self._url,
                    json=payload,
                    timeout=self._timeout,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
                if not isinstance(data, dict):
                    raise ValueError("Invalid JSON-RPC response")
                return data
            except Exception as e:
                last_exc = e
                if attempt >= self._max_retries:
                    break
        raise RuntimeError(f"RPC request failed: {last_exc}")

    def call(self, method: str, params: Sequence[Any]) -> Any:
        req_id = self._next_id
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": list(params)}
        data = self._post(payload)
        if "error" in data and data["error"] is not None:
            raise RuntimeError(f"RPC error: {data['error']}")
        return data.get("result")

    def eth_getCode(self, address: str, block: str) -> str:
        return str(self.call("eth_getCode", [address, block]))

    def eth_getStorageAt(self, address: str, slot: str, block: str) -> str:
        return str(self.call("eth_getStorageAt", [address, slot, block]))

    def eth_call(self, to: str, data: str, block: str) -> str:
        return str(self.call("eth_call", [{"to": to, "data": data}, block]))


@dataclass(frozen=True)
class RiskFlag:
    id: str
    severity: str
    message: str

    def to_json(self) -> Dict[str, str]:
        return {"id": self.id, "severity": self.severity, "message": self.message}


def _risk_score(flags: List[RiskFlag]) -> int:
    weights = {"HIGH": 4, "MEDIUM": 2, "LOW": 1}
    score = sum(weights.get(f.severity, 0) for f in flags)
    return min(10, score)


def _sort_flags(flags: List[RiskFlag]) -> List[RiskFlag]:
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(flags, key=lambda f: (order.get(f.severity, 999), f.id))


def analyze_proxy(
    provider: JsonRpcProvider,
    *,
    proxy_address: str,
    block: str,
    check_uups: bool,
    check_beacon_impl: bool,
) -> Dict[str, Any]:
    proxy_address = _normalize_address(proxy_address)

    code = provider.eth_getCode(proxy_address, block)
    if not isinstance(code, str):
        code = str(code)

    if code in ("0x", "0X", "") or len(_strip_0x(code)) == 0:
        flags = [
            RiskFlag(
                id="proxy_has_no_code",
                severity="HIGH",
                message="Proxy address has no contract code at the requested block",
            )
        ]
        flags = _sort_flags(flags)
        return {
            "demo": False,
            "proxy_address": proxy_address,
            "proxy_type": "NOT_A_CONTRACT",
            "implementation_address": None,
            "admin_address": None,
            "beacon_address": None,
            "beacon_implementation_address": None,
            "is_uups": None,
            "risk_score": _risk_score(flags),
            "risk_flags": [f.to_json() for f in flags],
        }

    impl_from_minimal = _match_eip1167_minimal_proxy(code)
    if impl_from_minimal is not None:
        implementation_address = impl_from_minimal
        flags: List[RiskFlag] = []

        impl_code = provider.eth_getCode(implementation_address, block)
        if impl_code in ("0x", "0X", "") or len(_strip_0x(impl_code)) == 0:
            flags.append(
                RiskFlag(
                    id="implementation_has_no_code",
                    severity="HIGH",
                    message="Implementation address has no contract code",
                )
            )

        flags = _sort_flags(flags)
        return {
            "demo": False,
            "proxy_address": proxy_address,
            "proxy_type": "EIP-1167_MINIMAL",
            "upgradable": False,
            "implementation_address": implementation_address,
            "admin_address": None,
            "beacon_address": None,
            "beacon_implementation_address": None,
            "is_uups": None,
            "risk_score": _risk_score(flags),
            "risk_flags": [f.to_json() for f in flags],
        }

    impl_slot = provider.eth_getStorageAt(proxy_address, EIP1967_IMPLEMENTATION_SLOT, block)
    admin_slot = provider.eth_getStorageAt(proxy_address, EIP1967_ADMIN_SLOT, block)
    beacon_slot = provider.eth_getStorageAt(proxy_address, EIP1967_BEACON_SLOT, block)

    implementation_address = _parse_storage_address(impl_slot)
    admin_address = _parse_storage_address(admin_slot)
    beacon_address = _parse_storage_address(beacon_slot)

    proxy_type = "UNKNOWN"
    beacon_implementation_address: Optional[str] = None

    if beacon_address is not None:
        proxy_type = "EIP-1967_BEACON"
        if check_beacon_impl:
            try:
                ret = provider.eth_call(beacon_address, SELECTOR_IMPLEMENTATION, block)
                beacon_implementation_address = _parse_return_address(ret)
            except Exception:
                beacon_implementation_address = None
    elif implementation_address is not None:
        proxy_type = "EIP-1967_PROXY"

    is_uups: Optional[bool] = None
    flags: List[RiskFlag] = []

    # Risk flags
    if proxy_type == "EIP-1967_PROXY":
        if implementation_address is None:
            flags.append(
                RiskFlag(
                    id="implementation_is_zero",
                    severity="HIGH",
                    message="EIP-1967 implementation slot is zero",
                )
            )
        else:
            impl_code = provider.eth_getCode(implementation_address, block)
            if impl_code in ("0x", "0X", "") or len(_strip_0x(impl_code)) == 0:
                flags.append(
                    RiskFlag(
                        id="implementation_has_no_code",
                        severity="HIGH",
                        message="Implementation address has no contract code",
                    )
                )

        if admin_address is None:
            flags.append(
                RiskFlag(
                    id="admin_is_zero",
                    severity="MEDIUM",
                    message="EIP-1967 admin slot is zero",
                )
            )
        else:
            admin_code = provider.eth_getCode(admin_address, block)
            if admin_code in ("0x", "0X", "") or len(_strip_0x(admin_code)) == 0:
                flags.append(
                    RiskFlag(
                        id="admin_is_eoa",
                        severity="LOW",
                        message="Admin address has no contract code (EOA or predeploy)",
                    )
                )

    if beacon_address is not None:
        beacon_code = provider.eth_getCode(beacon_address, block)
        if beacon_code in ("0x", "0X", "") or len(_strip_0x(beacon_code)) == 0:
            flags.append(
                RiskFlag(
                    id="beacon_has_no_code",
                    severity="HIGH",
                    message="Beacon address has no contract code",
                )
            )

    # UUPS detection (optional)
    if check_uups and implementation_address is not None:
        try:
            ret = provider.eth_call(implementation_address, SELECTOR_PROXIABLE_UUID, block)
            if isinstance(ret, str) and ret.lower().startswith("0x") and len(_strip_0x(ret)) >= 64:
                # Compare the 32-byte value to the implementation slot constant.
                got = "0x" + _strip_0x(ret).lower()[:64]
                expected = "0x" + _strip_0x(EIP1967_IMPLEMENTATION_SLOT).lower()[-64:]
                is_uups = got == expected
            else:
                is_uups = False
        except Exception:
            is_uups = None
            flags.append(
                RiskFlag(
                    id="uups_expected_but_missing",
                    severity="MEDIUM",
                    message="Failed to confirm UUPS via proxiableUUID()",
                )
            )

    flags = _sort_flags(flags)

    return {
        "demo": False,
        "proxy_address": proxy_address,
        "proxy_type": proxy_type,
        "upgradable": proxy_type in {"EIP-1967_PROXY", "EIP-1967_BEACON"},
        "implementation_address": implementation_address,
        "admin_address": admin_address,
        "beacon_address": beacon_address,
        "beacon_implementation_address": beacon_implementation_address,
        "is_uups": is_uups,
        "risk_score": _risk_score(flags),
        "risk_flags": [f.to_json() for f in flags],
    }


class _FakeProvider:
    def __init__(self, *, code: Dict[str, str], storage: Dict[Tuple[str, str], str], calls: Dict[Tuple[str, str], str]):
        self._code = {k.lower(): v for k, v in code.items()}
        self._storage = {(a.lower(), s.lower()): v for (a, s), v in storage.items()}
        self._calls = {(to.lower(), data.lower()): v for (to, data), v in calls.items()}

    def eth_getCode(self, address: str, block: str) -> str:
        return self._code.get(address.lower(), "0x")

    def eth_getStorageAt(self, address: str, slot: str, block: str) -> str:
        return self._storage.get((address.lower(), slot.lower()), "0x0")

    def eth_call(self, to: str, data: str, block: str) -> str:
        key = (to.lower(), data.lower())
        if key not in self._calls:
            raise RuntimeError("revert")
        return self._calls[key]


def _demo() -> Dict[str, Any]:
    # Addresses are illustrative.
    proxy1967 = "0x1111111111111111111111111111111111111111"
    impl1967 = "0x2222222222222222222222222222222222222222"
    admin1967 = "0x3333333333333333333333333333333333333333"

    proxy_min = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    impl_min = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    not_contract = "0x9999999999999999999999999999999999999999"

    # Minimal proxy runtime code with embedded implementation.
    minimal_code = (
        "0x363d3d373d3d3d363d73" + impl_min[2:] + "5af43d82803e903d91602b57fd5bf3"
    )

    def word(addr: str) -> str:
        return "0x" + ("00" * 12) + addr[2:].lower()

    fake = _FakeProvider(
        code={
            proxy1967: "0x60006000deadbeef",  # any non-empty code
            impl1967: "0x60006000cafebabe",  # any non-empty code
            admin1967: "0x",  # EOA (no code)
            proxy_min: minimal_code,
            impl_min: "0x6000",  # any non-empty code
            not_contract: "0x",
        },
        storage={
            (proxy1967, EIP1967_IMPLEMENTATION_SLOT): word(impl1967),
            (proxy1967, EIP1967_ADMIN_SLOT): word(admin1967),
            (proxy1967, EIP1967_BEACON_SLOT): "0x0",
        },
        calls={
            # proxiableUUID() returns the implementation slot constant
            (impl1967, SELECTOR_PROXIABLE_UUID): "0x" + _strip_0x(EIP1967_IMPLEMENTATION_SLOT).lower().rjust(64, "0"),
        },
    )

    # Use the same analyzer with the fake provider.
    examples = []

    for addr, label in [
        (proxy1967, "eip-1967-proxy"),
        (proxy_min, "eip-1167-minimal"),
        (not_contract, "not-a-contract"),
    ]:
        result = analyze_proxy(  # type: ignore[arg-type]
            fake,  # provider
            proxy_address=addr,
            block="latest",
            check_uups=True,
            check_beacon_impl=True,
        )
        result["label"] = label
        examples.append(result)

    return {"demo": True, "examples": examples}


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect EVM proxy patterns and upgrade risks")
    parser.add_argument("--demo", action="store_true", help="Run demo mode (offline)")
    parser.add_argument("--params", type=str, help="JSON parameters")
    args = parser.parse_args()

    try:
        if args.demo:
            print(_success(_demo()))
            return 0

        if args.params:
            params = json.loads(args.params)
            if not isinstance(params, dict):
                raise ValueError("--params JSON must be an object")
        else:
            stdin_params = _read_stdin_json()
            if stdin_params is None:
                print(_error("Either --demo, --params, or stdin JSON must be provided"))
                return 2
            params = stdin_params

        rpc_url = params.get("rpc_url")
        proxy_address = params.get("proxy_address")
        if not isinstance(rpc_url, str) or not rpc_url.strip():
            raise ValueError("rpc_url is required")
        if not isinstance(proxy_address, str) or not proxy_address.strip():
            raise ValueError("proxy_address is required")

        block = _normalize_block(params.get("block", "latest"))

        timeout_seconds = params.get("timeout_seconds", 20)
        if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")

        check_uups = params.get("check_uups", True)
        if not isinstance(check_uups, bool):
            raise ValueError("check_uups must be boolean")

        check_beacon_impl = params.get("check_beacon_impl", True)
        if not isinstance(check_beacon_impl, bool):
            raise ValueError("check_beacon_impl must be boolean")

        provider = JsonRpcProvider(rpc_url, timeout_seconds=timeout_seconds, max_retries=1)

        report = analyze_proxy(
            provider,
            proxy_address=str(proxy_address),
            block=block,
            check_uups=check_uups,
            check_beacon_impl=check_beacon_impl,
        )
        print(_success(report))
        return 0

    except json.JSONDecodeError as e:
        print(_error("Invalid JSON", {"message": str(e)}))
        return 1
    except ValueError as e:
        print(_error(str(e)))
        return 1
    except RuntimeError as e:
        print(_error(str(e)))
        return 1
    except Exception as e:
        print(_error("Unexpected error", {"message": str(e)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
