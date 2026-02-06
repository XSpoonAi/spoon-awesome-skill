#!/usr/bin/env python3
"""
Example: Check MEV risk before Uniswap swap

This example demonstrates how to use the MEV simulator to check
if a Uniswap swap is safe from MEV attacks.
"""

import json
import subprocess
import sys

# Example: Swap 10 ETH for USDC on Uniswap V2
tx_data = {
    "tx_data": {
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2 Router
        "data": "0x",  # Swap function call data would go here
        "value": "0x8AC7230489E80000",  # 10 ETH in hex
        "gas": "0x30000"
    },
    "chain": "ethereum",
    "slippage_tolerance": 0.5
}

# Run MEV simulator
result = subprocess.run(
    [sys.executable, "../scripts/mev_simulator.py"],
    input=json.dumps(tx_data),
    capture_output=True,
    text=True
)

if result.returncode == 0:
    analysis = json.loads(result.stdout)
    
    print("=" * 60)
    print("MEV RISK ANALYSIS")
    print("=" * 60)
    print(f"\nRisk Score: {analysis['risk_score']}/100")
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"\nEstimated MEV Loss: {analysis['estimated_mev_loss_eth']} ETH (${analysis['estimated_mev_loss_usd']})")
    
    print("\n🚨 Detected Risks:")
    for risk in analysis['detected_risks']:
        print(f"  - {risk}")
    
    print("\n💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  - {rec}")
    
    print("\n" + "=" * 60)
    
    # Decision logic
    if analysis['risk_score'] >= 70:
        print("⚠️  HIGH RISK - Strongly recommend using Flashbots!")
    elif analysis['risk_score'] >= 40:
        print("⚠️  MEDIUM RISK - Consider using Flashbots")
    else:
        print("✅ LOW RISK - Safe to submit normally")
    
else:
    print("Error running MEV simulator:")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    sys.exit(1)
