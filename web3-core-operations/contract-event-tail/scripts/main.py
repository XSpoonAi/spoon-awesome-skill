#!/usr/bin/env python3
"""Contract Event Tail - Monitor and retrieve contract events"""
import json
import sys
import os
import urllib.request
from typing import Dict, List, Optional
from datetime import datetime, timezone

CHAIN_CONFIGS = {
    "ethereum": {"api_url": "https://api.etherscan.io/api", "api_key_env": "ETHERSCAN_API_KEY"},
    "polygon": {"api_url": "https://api.polygonscan.com/api", "api_key_env": "POLYGONSCAN_API_KEY"},
    "arbitrum": {"api_url": "https://api.arbiscan.io/api", "api_key_env": "ARBISCAN_API_KEY"},
    "optimism": {"api_url": "https://api-optimistic.etherscan.io/api", "api_key_env": "OPTIMISM_API_KEY"},
}

def fetch_events(contract: str, from_block: int, to_block: int, chain: str) -> Dict:
    """Fetch contract events from block explorer"""
    config = CHAIN_CONFIGS.get(chain.lower())
    if not config:
        return {"error": f"Unsupported chain: {chain}"}
    
    api_key = os.getenv(config["api_key_env"])
    params = {
        "module": "logs",
        "action": "getLogs",
        "address": contract,
        "fromBlock": from_block,
        "toBlock": to_block,
        "page": 1,
        "offset": 1000
    }
    if api_key:
        params["apikey"] = api_key
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{config['api_url']}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        contract = input_data.get("contract_address")
        from_block = int(input_data.get("from_block", 0))
        to_block = int(input_data.get("to_block", 99999999))
        chain = input_data.get("chain", "ethereum")
        
        if not contract:
            print(json.dumps({"error": "contract_address required"}))
            return
        
        response = fetch_events(contract, from_block, to_block, chain)
        events = response.get("result", []) if isinstance(response.get("result"), list) else []
        
        result = {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contract": contract,
            "chain": chain,
            "events": events[:100],
            "total_events": len(events)
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
