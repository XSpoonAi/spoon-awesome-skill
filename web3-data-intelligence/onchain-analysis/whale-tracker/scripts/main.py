#!/usr/bin/env python3
"""Track large wallet movements and whale activity with real blockchain data"""
import json
import argparse
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from collections import defaultdict


def format_success(data):
    return json.dumps({"ok": True, "data": data}, ensure_ascii=False)


def format_error(error, details=None):
    result = {"ok": False, "error": error}
    if details:
        result["details"] = details
    return json.dumps(result, ensure_ascii=False)


def get_rpc_endpoint(network="ethereum"):
    """Get RPC endpoint for network."""
    endpoints = {
        "ethereum": "https://eth.llamarpc.com",
        "polygon": "https://polygon-rpc.com",
    }
    return endpoints.get(network, "")


def fetch_address_balance(address, network="ethereum", block="latest"):
    """Fetch ETH balance for an address."""
    rpc_url = get_rpc_endpoint(network)
    if not rpc_url:
        return None
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        req_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, block],
            "id": 1
        }).encode('utf-8')
        
        req = urllib.request.Request(
            rpc_url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req, context=ssl_context, timeout=5)
        result = json.loads(response.read())
        
        if "result" in result:
            balance_wei = int(result["result"], 16)
            return {
                "balance_wei": balance_wei,
                "balance_eth": balance_wei / 1e18
            }
        return None
    
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def fetch_transaction_count(address, network="ethereum"):
    """Fetch transaction count for an address."""
    rpc_url = get_rpc_endpoint(network)
    if not rpc_url:
        return None
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        req_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getTransactionCount",
            "params": [address, "latest"],
            "id": 1
        }).encode('utf-8')
        
        req = urllib.request.Request(
            rpc_url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req, context=ssl_context, timeout=5)
        result = json.loads(response.read())
        
        if "result" in result:
            return int(result["result"], 16)
        return None
    
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def fetch_erc20_transfers(address, network="ethereum"):
    """Fetch ERC20 Transfer events for whale address via eth_getLogs."""
    try:
        rpc_url = get_rpc_endpoint(network)
        if not rpc_url:
            return []
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Transfer event signature: keccak256("Transfer(address,address,uint256)")
        transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        padded_addr = "0x" + address[2:].zfill(64)
        
        # Fetch logs where whale is from or to address
        req_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [{
                "fromBlock": "latest",
                "toBlock": "latest",
                "topics": [transfer_topic, [padded_addr, padded_addr]]
            }],
            "id": 1
        }).encode('utf-8')
        
        req = urllib.request.Request(
            rpc_url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req, context=ssl_context, timeout=5)
        result = json.loads(response.read())
        
        if "result" in result:
            transfers = []
            for log in result["result"][:20]:
                transfers.append({
                    "token": log.get("address", "unknown"),
                    "from": log["topics"][1][2:].zfill(40) if len(log["topics"]) > 1 else "unknown",
                    "to": log["topics"][2][2:].zfill(40) if len(log["topics"]) > 2 else "unknown",
                    "value": log.get("data", "0x0"),
                    "block": int(log.get("blockNumber", "0x0"), 16)
                })
            return transfers
        return []
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return []


def classify_whale_behavior(address, transfers, balance_eth, tx_count):
    """Classify whale behavior: accumulating, distributing, or trading."""
    if not transfers or tx_count == 0:
        return "holding"
    
    # Major exchange deposit addresses
    exchange_addresses = {
        "3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "binance",
        "be0eb53f46cd790cd13851d5eff43d12404d33e8": "binance",
        "4d67bcf1b7dc0b6aa9ab1f21ad91485a1a36eafb": "kraken",
        "fbb1b73c4f0bda4f67dca266ce6ef42f520fbe2a": "coinbase",
        "71c7656ec7ab88b098defb751b7401b5f6d8976f": "ethereum_bridge",
    }
    
    # Count transfers to/from exchanges
    outflows = sum(1 for t in transfers if t.get("to", "").lower() in exchange_addresses)
    inflows = sum(1 for t in transfers if t.get("from", "").lower() in exchange_addresses)
    
    if outflows > inflows:
        return "distributing"
    elif inflows > outflows:
        return "accumulating"
    else:
        return "trading"


def analyze_whales(params):
    """Analyze whale movements with real or custom data."""
    network = params.get("network", "ethereum")
    use_api = params.get("use_api", True)
    threshold_usd = params.get("threshold_usd", 1000000)
    
    if use_api:
        # Fetch real balance data from blockchain with transfer tracking
        addresses = params.get("addresses", [])
        movements = []
        whale_behaviors = {}
        
        for addr in addresses[:50]:  # Limit to 50 addresses
            addr = addr.lower() if addr.startswith("0x") else f"0x{addr}"
            
            balance_data = fetch_address_balance(addr, network)
            tx_count = fetch_transaction_count(addr, network) or 0
            transfers = fetch_erc20_transfers(addr, network) if use_api else []
            
            if balance_data:
                balance_eth = balance_data["balance_eth"]
                balance_usd = balance_eth * 2000  # Approx USD value
                
                # Classify whale behavior based on recent transfers
                behavior = classify_whale_behavior(addr, transfers, balance_eth, tx_count)
                whale_behaviors[addr] = behavior
                
                movement = {
                    "address": addr,
                    "balance_eth": round(balance_eth, 6),
                    "balance_usd": round(balance_usd, 2),
                    "transaction_count": tx_count,
                    "activity_level": "active" if tx_count > 100 else "low_activity",
                    "behavior": behavior,
                    "recent_transfers": len(transfers),
                }
                
                # Add latest transfer if available
                if transfers:
                    movement["last_transfer_block"] = transfers[0].get("block", 0)
                    movement["token_activity"] = "recent"
                else:
                    movement["token_activity"] = "none"
                
                movements.append(movement)
        
        source = "blockchain_api_with_transfers"
    else:
        # Use provided movement data
        movements = params.get("movements", [])
        whale_behaviors = {m.get("address"): m.get("behavior", "unknown") for m in movements}
        source = "parameters"
    
    # Filter by threshold
    filtered = [m for m in movements if m.get("balance_usd", 0) >= threshold_usd]
    
    if not filtered:
        return {
            "status": "success",
            "source": source,
            "network": network,
            "threshold_usd": threshold_usd,
            "whale_count": 0,
            "whales": [],
            "total_whale_volume": 0,
            "activity_summary": {},
            "behavior_analysis": {},
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Categorize whales by balance
    mega_whales = [w for w in filtered if w.get("balance_usd", 0) >= 50000000]
    large_whales = [w for w in filtered if 10000000 <= w.get("balance_usd", 0) < 50000000]
    medium_whales = [w for w in filtered if 1000000 <= w.get("balance_usd", 0) < 10000000]
    
    # Activity analysis
    activity_counts = defaultdict(int)
    for m in filtered:
        activity = m.get("activity_level", "unknown")
        activity_counts[activity] += 1
    
    # Behavior analysis
    behavior_counts = defaultdict(int)
    for m in filtered:
        behavior = m.get("behavior", "unknown")
        behavior_counts[behavior] += 1
    
    # Top whales by balance
    top_whales = sorted(filtered, key=lambda x: x.get("balance_usd", 0), reverse=True)[:20]
    
    # Calculate metrics
    total_whale_vol = sum(m.get("balance_usd", 0) for m in filtered)
    avg_whale_vol = total_whale_vol / len(filtered) if filtered else 0
    total_transfers = sum(m.get("recent_transfers", 0) for m in filtered)
    
    result = {
        "status": "success",
        "source": source,
        "network": network,
        "threshold_usd": threshold_usd,
        "whale_count": len(filtered),
        "whale_categories": {
            "mega_whales": len(mega_whales),
            "large_whales": len(large_whales),
            "medium_whales": len(medium_whales)
        },
        "total_whale_volume_usd": round(total_whale_vol, 2),
        "avg_whale_balance_usd": round(avg_whale_vol, 2),
        "activity_summary": dict(activity_counts),
        "behavior_analysis": dict(behavior_counts),
        "top_whales": top_whales,
        "total_tx_count": sum(m.get("transaction_count", 0) for m in filtered),
        "avg_tx_per_whale": round(sum(m.get("transaction_count", 0) for m in filtered) / len(filtered), 1) if filtered else 0,
        "total_recent_transfers": total_transfers,
        "concentration_ratio": round((filtered[0].get("balance_usd", 0) / total_whale_vol * 100), 2) if filtered and total_whale_vol > 0 else 0,
        "whale_addresses": [m["address"] for m in top_whales],
        "whale_movements": {m["address"]: {"behavior": m.get("behavior"), "transfers": m.get("recent_transfers", 0)} for m in top_whales},
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Track whale wallet movements')
    parser.add_argument('--params', type=str, required=True, help='JSON parameters')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
        result = analyze_whales(params)
        print(format_success(result))
    
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
