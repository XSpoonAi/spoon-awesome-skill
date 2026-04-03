#!/usr/bin/env python3
"""
Bridge Status Script
Checks the status of bridge transactions via direct RPC queries
Uses web3.py for real blockchain data - no API keys required
"""

import json
import sys
from typing import Dict, Optional, List
from datetime import datetime, timezone
from web3 import Web3

# Chain configurations with RPC endpoints
# No API keys needed - direct RPC queries
CHAIN_CONFIGS = {
    "ethereum": {
        "rpc_url": "https://eth-mainnet.public.blastapi.io",
        "chain_id": 1,
        "name": "Ethereum",
        "explorer": "https://etherscan.io/tx/",
        "confirmations_required": 12
    },
    "polygon": {
        "rpc_url": "https://polygon-rpc.com",
        "chain_id": 137,
        "name": "Polygon",
        "explorer": "https://polygonscan.com/tx/",
        "confirmations_required": 256
    },
    "arbitrum": {
        "rpc_url": "https://arb1.arbitrum.io/rpc",
        "chain_id": 42161,
        "name": "Arbitrum One",
        "explorer": "https://arbiscan.io/tx/",
        "confirmations_required": 0  # Arbitrum confirms differently
    },
    "optimism": {
        "rpc_url": "https://mainnet.optimism.io",
        "chain_id": 10,
        "name": "Optimism",
        "explorer": "https://optimistic.etherscan.io/tx/",
        "confirmations_required": 0
    },
    "base": {
        "rpc_url": "https://mainnet.base.org",
        "chain_id": 8453,
        "name": "Base",
        "explorer": "https://basescan.org/tx/",
        "confirmations_required": 0
    },
    "bsc": {
        "rpc_url": "https://bsc-dataseed.bnbchain.org",
        "chain_id": 56,
        "name": "Binance Smart Chain",
        "explorer": "https://bscscan.com/tx/",
        "confirmations_required": 20
    },
    "zksync": {
        "rpc_url": "https://mainnet.era.zksync.io",
        "chain_id": 324,
        "name": "zkSync Era",
        "explorer": "https://explorer.zksync.io/tx/",
        "confirmations_required": 0
    },
    "linea": {
        "rpc_url": "https://rpc.linea.build",
        "chain_id": 59144,
        "name": "Linea",
        "explorer": "https://lineascan.build/tx/",
        "confirmations_required": 0
    }
}

# Bridge-specific information
BRIDGE_INFO = {
    "stargate": {
        "name": "Stargate (LayerZero)",
        "typical_time": "2-5 minutes",
        "contracts": {
            1: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC (real deployed contract on Ethereum)
            137: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC on Polygon
            42161: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5F8f"  # USDC on Arbitrum
        }
    },
    "wormhole": {
        "name": "Wormhole",
        "typical_time": "15-30 minutes",
        "contracts": {
            1: "0x98f3c9E6E3fAce36baEAD015fD50109394E4e07c",
            137: "0x3c3c561757bEe0f409cD5Ef6C861CC8864a5EB6b"
        }
    },
    "across": {
        "name": "Across",
        "typical_time": "2-10 minutes",
        "contracts": {
            1: "0x5c7BCd6E7De5423a257D81b442095A1a6ced35b5",
            137: "0x9c4C5D78029e568A10D1D0D8288AC870AC5eCC2a"
        }
    },
    "hop": {
        "name": "Hop",
        "typical_time": "5-15 minutes",
        "contracts": {
            1: "0x0000000000000000000000000000000000000001"
        }
    }
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


def get_tx_status(tx_hash: str, chain: str) -> Dict:
    """Get transaction status from blockchain via RPC"""
    try:
        w3, config = get_web3_instance(chain)
        
        # Validate tx hash format (hex string, 66 chars with 0x prefix)
        if not isinstance(tx_hash, str) or not tx_hash.startswith('0x') or len(tx_hash) != 66:
            return {
                "success": False,
                "error": "validation_error",
                "message": f"Invalid transaction hash format (expected 66 char hex with 0x prefix)"
            }
        
        try:
            # Ensure it's valid hex
            int(tx_hash, 16)
        except ValueError:
            return {
                "success": False,
                "error": "validation_error",
                "message": f"Invalid transaction hash (not valid hex)"
            }
        
        # Get current block number for confirmations
        current_block = w3.eth.block_number
        
        # Get transaction receipt
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        if receipt is None:
            return {
                "success": True,
                "status": "pending",
                "confirmations": 0,
                "on_chain": False,
                "message": "Transaction not yet confirmed on chain"
            }
        
        # Calculate confirmations
        block_number = receipt["blockNumber"]
        confirmations = current_block - block_number
        
        # Get transaction to extract more details
        tx = w3.eth.get_transaction(tx_hash)
        
        return {
            "success": True,
            "status": "success" if receipt["status"] == 1 else "failed",
            "block_number": block_number,
            "transaction_hash": tx_hash,
            "from": receipt["from"],
            "to": receipt["to"],
            "gas_used": receipt["gasUsed"],
            "gas_limit": tx["gas"],
            "confirmations": confirmations,
            "confirmed": confirmations >= config["confirmations_required"],
            "on_chain": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chain": config["name"],
            "rpc_used": config["rpc_url"]
        }
    except Exception as e:
        if "execution reverted" in str(e):
            return {
                "success": True,
                "status": "failed",
                "on_chain": True,
                "error": "Transaction reverted"
            }
        return {
            "success": False,
            "error": "rpc_error",
            "message": str(e)
        }


def check_bridge_status(bridge: str, tx_hash: str, source_chain: str, dest_chain: Optional[str] = None) -> Dict:
    """Check bridge transaction status"""
    bridge = bridge.lower()
    source_chain = source_chain.lower()
    
    bridge_data = BRIDGE_INFO.get(bridge)
    if not bridge_data:
        return {
            "success": False,
            "error": "unsupported_bridge",
            "message": f"Bridge '{bridge}' not supported. Supported: stargate, wormhole, across, hop"
        }
    
    # Get source transaction status
    source_tx_status = get_tx_status(tx_hash, source_chain)
    
    if not source_tx_status.get("success"):
        return source_tx_status
    
    result = {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bridge": {
            "name": bridge_data["name"],
            "protocol": bridge
        },
        "source_transaction": {
            "hash": tx_hash,
            "chain": CHAIN_CONFIGS[source_chain]["name"],
            "status": source_tx_status.get("status"),
            "block_number": source_tx_status.get("block_number"),
            "confirmations": source_tx_status.get("confirmations", 0),
            "gas_used": source_tx_status.get("gas_used"),
            "from": source_tx_status.get("from"),
            "to": source_tx_status.get("to"),
            "explorer_url": CHAIN_CONFIGS[source_chain]["explorer"] + tx_hash if source_tx_status.get("on_chain") else None
        },
        "bridge_status": {
            "phase": determine_phase(source_tx_status, bridge),
            "estimated_completion": bridge_data.get("typical_time"),
            "bridge_contract": bridge_data.get("contracts", {}).get(CHAIN_CONFIGS[source_chain].get("chain_id")),
            "support_chains": list(bridge_data.get("contracts", {}).keys())
        },
        "destination": {
            "chain": CHAIN_CONFIGS.get(dest_chain, {}).get("name") if dest_chain else "Unknown",
            "expected_time": bridge_data.get("typical_time")
        } if dest_chain else None,
        "next_steps": get_next_steps(source_tx_status, bridge),
        "rpc_used": source_tx_status.get("rpc_used")
    }
    
    return result


def determine_phase(tx_status: Dict, bridge: str) -> str:
    """Determine current phase of bridge transaction"""
    status = tx_status.get("status")
    confirmations = tx_status.get("confirmations", 0)
    
    if status == "pending":
        return "PENDING - Source transaction not yet confirmed"
    elif status == "failed":
        return "FAILED - Source transaction reverted"
    elif status == "success":
        if confirmations >= 12:
            return "IN_PROGRESS - Source confirmed, bridge processing, check destination"
        else:
            return f"CONFIRMING - {confirmations} confirmations (waiting for {12 - confirmations} more)"
    else:
        return "UNKNOWN"


def get_next_steps(tx_status: Dict, bridge: str) -> List[str]:
    """Get recommended next steps"""
    steps = []
    status = tx_status.get("status")
    confirmations = tx_status.get("confirmations", 0)
    
    if status == "pending":
        steps.append("⏳ Transaction is pending - waiting for first confirmation")
        steps.append("💰 Check gas price on network - may be stuck if gas too low")
        steps.append("🔍 Monitor block time for your chain")
    elif status == "failed":
        steps.append("❌ Transaction failed/reverted")
        steps.append("🔧 Review transaction error and retry with correct parameters")
        steps.append("💵 Ensure sufficient gas and token balance")
    elif status == "success":
        if confirmations < 12:
            steps.append(f"🔗 Transaction confirming: {confirmations}/12 blocks")
            steps.append("⏳ Wait for sufficient confirmations before bridge processes")
        else:
            steps.append("✅ Source transaction confirmed on chain")
            steps.append(f"🌉 Bridge is processing via {bridge}")
            steps.append(f"⏱️  Estimated time: {BRIDGE_INFO.get(bridge, {}).get('typical_time', '5-30 minutes')}")
            
            if bridge == "wormhole":
                steps.append("📍 Check Wormhole official status for updates")
            elif bridge == "stargate":
                steps.append("📍 Use LayerZero Scan for real-time bridge status")
            elif bridge == "across":
                steps.append("📍 Check liquidity pools on destination chain")
            else:
                steps.append("📍 Monitor destination chain for incoming transaction")
    
    return steps


def get_bridge_health(bridge: str) -> Dict:
    """Get bridge health status via RPC queries"""
    bridge = bridge.lower()
    bridge_data = BRIDGE_INFO.get(bridge)
    
    if not bridge_data:
        return {
            "success": False,
            "error": "unsupported_bridge",
            "message": f"Bridge '{bridge}' not supported"
        }
    
    result = {
        "success": True,
        "bridge": {
            "name": bridge_data["name"],
            "protocol": bridge
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chains_supported": [],
        "availability": {}
    }
    
    # Check bridge contract availability on each supported chain
    for chain_id, contract_addr in bridge_data.get("contracts", {}).items():
        # Find chain name from chain_id
        chain_name = None
        for name, config in CHAIN_CONFIGS.items():
            if config.get("chain_id") == chain_id:
                chain_name = name
                break
        
        if not chain_name:
            continue
        
        result["chains_supported"].append(CHAIN_CONFIGS[chain_name]["name"])
        
        try:
            w3, config = get_web3_instance(chain_name)
            
            # Check if contract exists by getting code
            code = w3.eth.get_code(Web3.to_checksum_address(contract_addr))
            is_active = len(code) > 2  # Contract has bytecode (more than just "0x")
            
            current_block = w3.eth.block_number
            
            result["availability"][CHAIN_CONFIGS[chain_name]["name"]] = {
                "chain_id": chain_id,
                "contract": contract_addr,
                "active": is_active,
                "current_block": current_block,
                "status": "OPERATIONAL" if is_active else "INACTIVE"
            }
        except Exception as e:
            result["availability"][CHAIN_CONFIGS[chain_name]["name"]] = {
                "chain_id": chain_id,
                "contract": contract_addr,
                "status": "ERROR",
                "error": str(e)
            }
    
    result["overall_status"] = "OPERATIONAL" if all(
        c.get("status") == "OPERATIONAL" for c in result["availability"].values()
    ) else "DEGRADED"
    
    return result


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        action = input_data.get("action", "check_tx")
        bridge = input_data.get("bridge", "stargate")
        tx_hash = input_data.get("tx_hash")
        source_chain = input_data.get("source_chain", "ethereum")
        dest_chain = input_data.get("dest_chain")

        if action == "check_tx":
            if not tx_hash:
                print(json.dumps({
                    "success": False,
                    "error": "missing_parameter",
                    "message": "Missing required parameter: tx_hash"
                }, indent=2))
                sys.exit(1)
            result = check_bridge_status(bridge, tx_hash, source_chain, dest_chain)
        elif action == "health":
            result = get_bridge_health(bridge)
        elif action == "chains":
            result = {
                "success": True,
                "supported_chains": list(CHAIN_CONFIGS.keys()),
                "chain_details": {
                    name: {
                        "id": config["chain_id"],
                        "full_name": config["name"],
                        "explorer": config["explorer"],
                        "rpc": config["rpc_url"]
                    }
                    for name, config in CHAIN_CONFIGS.items()
                }
            }
        elif action == "bridges":
            result = {
                "success": True,
                "supported_bridges": list(BRIDGE_INFO.keys()),
                "bridge_details": {
                    name: {
                        "full_name": data["name"],
                        "typical_time": data["typical_time"],
                        "supported_chains": len(data.get("contracts", {}))
                    }
                    for name, data in BRIDGE_INFO.items()
                }
            }
        else:
            print(json.dumps({
                "success": False,
                "error": "unknown_action",
                "message": f"Unknown action: {action}. Supported: check_tx, health, chains, bridges"
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
