#!/bin/bash
# Token Approval Checker - Demo
# Usage: ETHERSCAN_API_KEY=xxx ./run_demo.sh
# Or use a public address to test (no key needed for a few calls, but rate limit may apply)

set -e
cd "$(dirname "$0")"

# Example: Ethereum Foundation (has token tx history)
ADDRESS="${1:-0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae}"
CHAIN="${2:-ethereum}"

echo "=== Token Approval Check ==="
echo "Address: $ADDRESS"
echo "Chain: $CHAIN"
echo ""
echo '{"address":"'"$ADDRESS"'","chain":"'"$CHAIN"'"}' | python3 approval_checker.py
