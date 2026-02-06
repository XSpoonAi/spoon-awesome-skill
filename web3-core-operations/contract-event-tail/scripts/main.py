#!/usr/bin/env python3
"""
Contract Event Tail - Monitor and retrieve contract events
Uses direct RPC eth_getLogs for real blockchain event queries
No API keys required
"""

import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from web3 import Web3
from eth_abi import decode
import re

# Chain configurations with RPC endpoints
CHAIN_CONFIGS = {
    "ethereum": {
        "rpc_url": "https://eth-mainnet.public.blastapi.io",
        "chain_id": 1,
        "name": "Ethereum",
        "block_time": 12  # seconds
    },
    "polygon": {
        "rpc_url": "https://polygon-rpc.com",
        "chain_id": 137,
        "name": "Polygon",
        "block_time": 2
    },
    "arbitrum": {
        "rpc_url": "https://arb1.arbitrum.io/rpc",
        "chain_id": 42161,
        "name": "Arbitrum One",
        "block_time": 0.25
    },
    "optimism": {
        "rpc_url": "https://mainnet.optimism.io",
        "chain_id": 10,
        "name": "Optimism",
        "block_time": 2
    },
    "base": {
        "rpc_url": "https://mainnet.base.org",
        "chain_id": 8453,
        "name": "Base",
        "block_time": 2
    },
    "bsc": {
        "rpc_url": "https://bsc-dataseed.bnbchain.org",
        "chain_id": 56,
        "name": "Binance Smart Chain",
        "block_time": 3
    }
}

# Common event signatures for quick lookup
COMMON_EVENTS = {
    "Transfer": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    "Approval": "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
    "Swap": "0xd78ad95fa46012529f48e5a17c6a6ee5edcf5cc4de798e919b15e8a1e2e1688f",  # Uniswap V2
    "SwapExactTokensForTokens": "0x1f1ff1f5fb41346850b2f5c04e6c767e2f1eb89743c720ade6f3f3de6869681c0"  # Uniswap V3
}


def get_web3_instance(chain: str) -> tuple:
    """Get Web3 instance for chain"""
    config = CHAIN_CONFIGS.get(chain.lower())
    if not config:
        raise ValueError(f"Unsupported chain: {chain}")
    
    try:
        w3 = Web3(Web3.HTTPProvider(config["rpc_url"], request_kwargs={"timeout": 30}))
        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to {chain} RPC")
        return w3, config
    except Exception as e:
        raise ConnectionError(f"RPC connection failed for {chain}: {e}")


def get_event_logs(
    contract_address: str,
    from_block: int,
    to_block: int,
    chain: str,
    topic0: Optional[str] = None,
    topic1: Optional[str] = None,
    topic2: Optional[str] = None,
    topic3: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch contract events via eth_getLogs RPC call
    Supports filtering by topics (event signature and indexed parameters)
    """
    try:
        w3, config = get_web3_instance(chain)
        
        # Validate contract address
        if not Web3.is_address(contract_address):
            return {
                "success": False,
                "error": "validation_error",
                "message": f"Invalid contract address format"
            }
        
        contract_address = Web3.to_checksum_address(contract_address)
        
        # Get current block
        current_block = w3.eth.block_number
        
        # Validate block range
        if from_block < 0:
            from_block = 0
        if to_block < 0 or to_block > current_block:
            to_block = current_block
        
        # Limit to 5000 block range for performance
        if (to_block - from_block) > 5000:
            to_block = from_block + 5000
        
        # Build filter topics
        topics = []
        for topic in [topic0, topic1, topic2, topic3]:
            if topic:
                # Normalize topic (ensure it's a valid 32-byte hex string)
                if not topic.startswith('0x'):
                    topic = '0x' + topic
                if len(topic) != 66:  # 0x + 64 hex chars
                    continue
                topics.append(topic)
        
        # Create filter dict
        filter_dict = {
            "address": contract_address,
            "fromBlock": from_block,
            "toBlock": to_block
        }
        
        if topics:
            filter_dict["topics"] = [topics] if len(topics) == 1 else [topics[:1], topics[1:] if len(topics) > 1 else None]
        
        # Get logs via RPC
        logs = w3.eth.get_logs(filter_dict)
        
        # Parse logs with metadata
        parsed_logs = []
        for log in logs:
            # Clean up topics and data to hex strings
            topics = []
            for topic in log["topics"]:
                if isinstance(topic, bytes):
                    topics.append('0x' + topic.hex())
                else:
                    topics.append(str(topic))
            
            data_str = log["data"]
            if isinstance(data_str, bytes):
                data_str = '0x' + data_str.hex()
            else:
                data_str = str(data_str)
            
            tx_hash_str = str(log["transactionHash"])
            if isinstance(log["transactionHash"], bytes):
                tx_hash_str = '0x' + log["transactionHash"].hex()
            
            block_hash_str = str(log["blockHash"])
            if isinstance(log["blockHash"], bytes):
                block_hash_str = '0x' + log["blockHash"].hex()
            
            parsed_log = {
                "address": str(log["address"]),
                "topics": topics,
                "data": data_str,
                "blockNumber": log["blockNumber"],
                "transactionHash": tx_hash_str,
                "transactionIndex": log["transactionIndex"],
                "blockHash": block_hash_str,
                "logIndex": log["logIndex"],
                "removed": log["removed"]
            }
            parsed_logs.append(parsed_log)
        
        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chain": config["name"],
            "contract": contract_address,
            "from_block": from_block,
            "to_block": to_block,
            "block_range": to_block - from_block + 1,
            "current_block": current_block,
            "total_events": len(logs),
            "events": parsed_logs,
            "filters_applied": {
                "topic0": topic0,
                "topic1": topic1,
                "topic2": topic2,
                "topic3": topic3
            },
            "rpc_used": config["rpc_url"]
        }
    except ValueError as e:
        return {
            "success": False,
            "error": "validation_error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "rpc_error",
            "message": str(e)
        }


def get_contract_info(contract_address: str, chain: str) -> Dict[str, Any]:
    """Get contract information from blockchain"""
    try:
        w3, config = get_web3_instance(chain)
        
        if not Web3.is_address(contract_address):
            return {
                "success": False,
                "error": "validation_error",
                "message": "Invalid contract address"
            }
        
        contract_address = Web3.to_checksum_address(contract_address)
        
        # Get contract code
        code = w3.eth.get_code(contract_address)
        is_contract = len(code) > 2
        
        # Get creation transaction (if possible)
        current_block = w3.eth.block_number
        
        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contract": contract_address,
            "chain": config["name"],
            "is_contract": is_contract,
            "code_length": len(code),
            "current_block": current_block,
            "rpc_used": config["rpc_url"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": "rpc_error",
            "message": str(e)
        }


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        
        action = input_data.get("action", "get_logs")
        contract = input_data.get("contract_address")
        chain = input_data.get("chain", "ethereum")
        
        # Handle listing actions that don't need contract
        if action == "events":
            print(json.dumps({
                "success": True,
                "common_events": COMMON_EVENTS,
                "note": "Use topic0 parameter to filter by event signature"
            }, indent=2))
            sys.exit(0)
        
        if action == "chains":
            print(json.dumps({
                "success": True,
                "supported_chains": list(CHAIN_CONFIGS.keys()),
                "chain_details": {
                    name: {
                        "id": config["chain_id"],
                        "name": config["name"],
                        "block_time": config["block_time"]
                    }
                    for name, config in CHAIN_CONFIGS.items()
                }
            }, indent=2))
            sys.exit(0)
        
        # All other actions require contract address
        if not contract:
            print(json.dumps({
                "success": False,
                "error": "missing_parameter",
                "message": "contract_address is required"
            }, indent=2))
            sys.exit(1)
        
        if action == "get_logs":
            from_block = int(input_data.get("from_block", 0))
            to_block = int(input_data.get("to_block", -1))
            topic0 = input_data.get("topic0")
            topic1 = input_data.get("topic1")
            topic2 = input_data.get("topic2")
            topic3 = input_data.get("topic3")
            
            result = get_event_logs(
                contract, from_block, to_block, chain,
                topic0, topic1, topic2, topic3
            )
        elif action == "info":
            result = get_contract_info(contract, chain)
        else:
            print(json.dumps({
                "success": False,
                "error": "unknown_action",
                "message": f"Unknown action: {action}. Supported: get_logs, info, events, chains"
            }, indent=2))
            sys.exit(1)
        
        print(json.dumps(result, indent=2))
    
    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "json_error",
            "message": "Invalid JSON input"
        }, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": "runtime_error",
            "message": str(e)
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
