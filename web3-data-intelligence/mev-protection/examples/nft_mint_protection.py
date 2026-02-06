#!/usr/bin/env python3
"""
Example: Analyze NFT mint frontrunning risk

This example demonstrates how to check if your NFT mint transaction
will be frontrun by bots.
"""

import json
import subprocess
import sys

# Example: Check frontrunning risk for NFT mint
input_data = {
    "tx_type": "nft_mint",
    "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",  # BAYC example
    "gas_price": "50000000000",  # 50 gwei
    "chain": "ethereum"
}

# Run frontrun analyzer
result = subprocess.run(
    [sys.executable, "../scripts/frontrun_analyzer.py"],
    input=json.dumps(input_data),
    capture_output=True,
    text=True
)

if result.returncode == 0:
    analysis = json.loads(result.stdout)
    
    print("=" * 60)
    print("FRONTRUNNING RISK ANALYSIS")
    print("=" * 60)
    print(f"\nTransaction Type: {analysis['tx_type']}")
    print(f"Contract: {analysis['contract_address']}")
    print(f"Chain: {analysis['chain']}")
    
    print(f"\n🎯 Risk Assessment:")
    print(f"  Frontrun Risk: {analysis['frontrun_risk']}")
    print(f"  Risk Score: {analysis['risk_score']}/100")
    print(f"  Success Probability: {analysis['estimated_success_probability'] * 100}%")
    
    print(f"\n⛽ Gas Analysis:")
    print(f"  Your Gas Price: {analysis.get('user_gas_price_gwei', 'N/A')} gwei")
    print(f"  Current Gas Price: {analysis.get('current_gas_price_gwei', 'N/A')} gwei")
    print(f"  Recommended Gas: {analysis['recommended_gas_price_gwei']} gwei")
    
    print(f"\n🤖 Competition:")
    print(f"  Competing Transactions: {analysis['competing_txs']}")
    
    print(f"\n⚠️  Risks:")
    for risk in analysis['risks']:
        print(f"  - {risk}")
    
    print("\n" + "=" * 60)
    
    # Decision logic
    if analysis['frontrun_risk'] in ['HIGH', 'VERY_HIGH']:
        print("🚨 HIGH FRONTRUNNING RISK!")
        print(f"💡 Recommendation: Increase gas to {analysis['recommended_gas_price_gwei']} gwei")
    else:
        print("✅ Moderate frontrunning risk - proceed with caution")
    
else:
    print("Error running frontrun analyzer:")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    sys.exit(1)
