#!/usr/bin/env python3
"""Cluster and analyze related transactions with real blockchain data"""
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


def fetch_transaction(tx_hash, network="ethereum"):
    """Fetch transaction details from blockchain RPC."""
    rpc_url = get_rpc_endpoint(network)
    if not rpc_url:
        return None
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        req_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [tx_hash],
            "id": 1
        }).encode('utf-8')
        
        req = urllib.request.Request(
            rpc_url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req, context=ssl_context, timeout=5)
        result = json.loads(response.read())
        
        if "result" not in result or result["result"] is None:
            return None
        
        tx = result["result"]
        return {
            "hash": tx.get("hash", ""),
            "from": tx.get("from", "").lower(),
            "to": tx.get("to", "").lower() if tx.get("to") else None,
            "value": tx.get("value", "0"),
            "gas": tx.get("gas", "0"),
            "gasPrice": tx.get("gasPrice", "0"),
            "nonce": int(tx.get("nonce", "0"), 16),
            "blockNumber": int(tx.get("blockNumber", "0"), 16) if tx.get("blockNumber") else None,
            "input": tx.get("input", "0x")
        }
    
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def analyze_tx_cluster(params):
    """Analyze transaction cluster with real or custom data."""
    network = params.get("network", "ethereum")
    use_api = params.get("use_api", True)
    
    if use_api:
        # Fetch real transaction data from blockchain
        tx_hashes = params.get("tx_hashes", [])
        transactions = []
        
        for tx_hash in tx_hashes[:50]:  # Limit to 50 txs per request
            tx = fetch_transaction(tx_hash, network)
            if tx:
                transactions.append(tx)
        
        source = "blockchain_api"
    else:
        # Use provided transaction data
        transactions = params.get("transactions", [])
        source = "parameters"
    
    if not transactions:
        return {
            "status": "success",
            "source": source,
            "network": network,
            "cluster_size": 0,
            "transactions": [],
            "unique_addresses": 0,
            "total_value_eth": 0,
            "pattern": "empty",
            "address_graph": {"nodes": [], "edges": []},
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Build address graph
    unique_addresses = set()
    address_graph_nodes = {}
    address_graph_edges = defaultdict(int)
    
    total_value_wei = 0
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    address_values = defaultdict(int)
    
    for tx in transactions:
        from_addr = tx.get("from", "unknown")
        to_addr = tx.get("to", "unknown") or "contract_creation"
        value_wei = int(tx.get("value", "0"), 16) if isinstance(tx.get("value"), str) else int(tx.get("value", 0))
        
        unique_addresses.add(from_addr)
        if to_addr != "contract_creation":
            unique_addresses.add(to_addr)
        
        # Track values
        total_value_wei += value_wei
        address_values[from_addr] -= value_wei
        if to_addr != "contract_creation":
            address_values[to_addr] += value_wei
        
        # Build graph
        out_degree[from_addr] += 1
        if to_addr != "contract_creation":
            in_degree[to_addr] += 1
            edge_key = f"{from_addr}->{to_addr}"
            address_graph_edges[edge_key] += 1
    
    # Create nodes with degree info
    for addr in unique_addresses:
        addr_type = "contract" if addr == "contract_creation" else "wallet"
        address_graph_nodes[addr] = {
            "address": addr,
            "type": addr_type,
            "in_degree": in_degree[addr],
            "out_degree": out_degree[addr],
            "net_flow_eth": round(address_values[addr] / 1e18, 6)
        }
    
    # Convert edges to list
    graph_edges = [
        {
            "from": edge.split("->")[0],
            "to": edge.split("->")[1],
            "count": count
        }
        for edge, count in sorted(address_graph_edges.items(), key=lambda x: x[1], reverse=True)[:20]
    ]
    
    # Detect pattern
    sources = [addr for addr, out in out_degree.items() if in_degree[addr] == 0 and out > 0]
    sinks = [addr for addr, inp in in_degree.items() if out_degree[addr] == 0 and inp > 0]
    
    if len(transactions) == 1:
        pattern = "single_transaction"
    elif len(sources) == 1 and len(sinks) > 1:
        pattern = "fan_out"  # Fund splitting
    elif len(sources) > 1 and len(sinks) == 1:
        pattern = "fan_in"   # Fund consolidation
    elif len(sources) == 1 and len(sinks) == 1:
        pattern = "chain"    # Linear sequence
    else:
        pattern = "complex"
    
    # Calculate cluster metrics
    avg_tx_value = total_value_wei / len(transactions) if transactions else 0
    
    result = {
        "status": "success",
        "source": source,
        "network": network,
        "cluster_size": len(transactions),
        "transactions_analyzed": len(transactions),
        "unique_addresses": len(unique_addresses),
        "total_value_wei": str(total_value_wei),
        "total_value_eth": round(total_value_wei / 1e18, 6),
        "avg_tx_value_eth": round(avg_tx_value / 1e18, 6),
        "pattern_type": pattern,
        "pattern_stats": {
            "source_addresses": len(sources),
            "sink_addresses": len(sinks),
            "intermediate_addresses": len(unique_addresses) - len(sources) - len(sinks)
        },
        "address_graph": {
            "nodes": list(address_graph_nodes.values()),
            "edges": graph_edges
        },
        "highest_value_addresses": sorted(
            [{"address": addr, "flow_eth": round(val / 1e18, 6)} for addr, val in address_values.items()],
            key=lambda x: abs(x["flow_eth"]),
            reverse=True
        )[:10],
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Cluster and analyze related transactions')
    parser.add_argument('--params', type=str, required=True, help='JSON parameters')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
        result = analyze_tx_cluster(params)
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
