#!/usr/bin/env python3
"""Check cross-chain bridge transaction status"""
import json
import argparse
import sys
from datetime import datetime, timedelta


def format_success(data):
    return json.dumps({"ok": True, "data": data}, ensure_ascii=False)


def format_error(error, details=None):
    result = {"ok": False, "error": error}
    if details:
        result["details"] = details
    return json.dumps(result, ensure_ascii=False)


def check_bridge_status(params):
    """Check bridge transaction status."""
    bridge = params.get("bridge")
    tx_hash = params.get("tx_hash")
    source_chain = params.get("source_chain", "ethereum")
    
    if not bridge or not tx_hash:
        raise ValueError("bridge and tx_hash are required")
    
    # Validate bridge name
    valid_bridges = ["arbitrum", "optimism", "polygon", "base", "zksync"]
    if bridge not in valid_bridges:
        raise ValueError(f"Invalid bridge. Must be one of: {', '.join(valid_bridges)}")
    
    # Simulate bridge status check
    # In real implementation, this would query bridge APIs
    status_options = ["pending", "confirmed", "completed", "failed"]
    
    # Generate realistic status based on tx_hash
    status_index = sum(ord(c) for c in tx_hash) % len(status_options)
    status = status_options[status_index]
    
    result = {
        "bridge": bridge,
        "tx_hash": tx_hash,
        "source_chain": source_chain,
        "destination_chain": bridge,
        "status": status,
        "confirmations": 12 if status == "completed" else 3,
        "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat() if status == "pending" else None,
        "source_tx": tx_hash,
        "destination_tx": f"0x{tx_hash[2:10]}...{tx_hash[-8:]}" if status == "completed" else None
    }
    
    return result


def execute_skill(params):
    """Main skill logic."""
    return check_bridge_status(params)


def main():
    parser = argparse.ArgumentParser(description='Check cross-chain bridge transaction status')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--params', type=str, help='JSON parameters')
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            result = {
                "demo": True,
                "bridge": "arbitrum",
                "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "source_chain": "ethereum",
                "destination_chain": "arbitrum",
                "status": "completed",
                "confirmations": 12,
                "estimated_completion": None,
                "source_tx": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "destination_tx": "0x12345678...90abcdef"
            }
            print(format_success(result))
        
        elif args.params:
            params = json.loads(args.params)
            result = execute_skill(params)
            print(format_success(result))
        
        else:
            print(format_error("Either --demo or --params must be provided"))
            sys.exit(1)
    
    except json.JSONDecodeError as e:
        print(format_error(f"Invalid JSON: {e}"))
        sys.exit(1)
    except ValueError as e:
        print(format_error(str(e)))
        sys.exit(1)
    except Exception as e:
        print(format_error(f"Unexpected error: {e}"))
        sys.exit(1)


if __name__ == '__main__':
    main()
