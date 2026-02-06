#!/usr/bin/env python3
"""
Example: Detect sandwich attack on historical transaction

This example shows how to analyze a past transaction to determine
if it was sandwiched by MEV bots.
"""

import json
import subprocess
import sys

# Example: Analyze a historical transaction
# Replace with actual transaction hash
tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

input_data = {
    "tx_hash": tx_hash,
    "chain": "ethereum"
}

# Run sandwich detector
result = subprocess.run(
    [sys.executable, "../scripts/sandwich_detector.py"],
    input=json.dumps(input_data),
    capture_output=True,
    text=True
)

if result.returncode == 0:
    analysis = json.loads(result.stdout)
    
    print("=" * 60)
    print("SANDWICH ATTACK ANALYSIS")
    print("=" * 60)
    print(f"\nTransaction: {analysis['tx_hash']}")
    print(f"Block: {analysis['block_number']}")
    print(f"Chain: {analysis['chain']}")
    
    if analysis['is_sandwiched']:
        print(f"\n🚨 SANDWICH ATTACK DETECTED!")
        print(f"Confidence: {analysis['confidence'] * 100}%")
        print(f"\nFrontrun TX: {analysis['frontrun_tx']}")
        print(f"Backrun TX: {analysis['backrun_tx']}")
        print(f"MEV Bot: {analysis['mev_bot_address']}")
        
        print(f"\n💸 Financial Impact:")
        print(f"  Victim Loss: {analysis['victim_loss_eth']} ETH (${analysis['victim_loss_usd']})")
        print(f"  Bot Profit: {analysis['bot_profit_eth']} ETH (${analysis['bot_profit_usd']})")
        
        print(f"\n📊 Pattern Details:")
        for key, value in analysis['pattern_details'].items():
            print(f"  {key}: {value}")
    else:
        print("\n✅ No sandwich attack detected")
        print(f"Reason: {analysis.get('reason', 'Transaction appears clean')}")
    
    print("\n" + "=" * 60)
    
else:
    print("Error running sandwich detector:")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    sys.exit(1)
