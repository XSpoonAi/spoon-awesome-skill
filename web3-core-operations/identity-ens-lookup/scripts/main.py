#!/usr/bin/env python3
"""Identity ENS Lookup - Resolve ENS names to addresses using REAL blockchain data"""
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Any

try:
    from web3 import Web3
    from eth_utils import is_checksum_address
except ImportError:
    Web3 = None

# RPC endpoint
RPC_URL = os.getenv("ETHEREUM_RPC", "https://eth-mainnet.public.blastapi.io")

# ENS Registry ABI
ENS_REGISTRY_ADDRESS = "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e"
ENS_REGISTRY_ABI = [
    {
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "owner",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "resolver",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ENS Resolver ABI (Public Resolver)
ENS_RESOLVER_ABI = [
    {
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "addr",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "node", "type": "bytes32"},
            {"name": "key", "type": "string"}
        ],
        "name": "text",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "node", "type": "bytes32"}],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Reverse Registrar ABI
REVERSE_REGISTRAR_ABI = [
    {
        "inputs": [{"name": "addr", "type": "address"}],
        "name": "node",
        "outputs": [{"name": "", "type": "bytes32"}],
        "stateMutability": "pure",
        "type": "function"
    }
]

def get_web3_client():
    """Get Web3 client with RPC connection"""
    if Web3 is None:
        raise RuntimeError("dependency_error: web3.py not installed. Install with: pip install web3")
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 30}))
        try:
            _ = w3.eth.block_number
        except Exception as e:
            raise ConnectionError(f"Failed to connect to RPC: {RPC_URL}. Error: {str(e)}")
        return w3
    except Exception as e:
        raise RuntimeError(f"connection_error: Failed to connect to blockchain RPC: {str(e)}")

def name_to_node(name: str) -> str:
    """Convert ENS name to namehash"""
    if not name:
        raise ValueError("ENS name cannot be empty")
    
    node = b'\x00' * 32
    labels = name.split('.')
    
    for label in reversed(labels):
        if not label:
            continue
        hash_obj = Web3.keccak(text=label)
        node = Web3.keccak(node + hash_obj)
    
    return '0x' + node.hex()

def resolve_ens_name(w3, name: str) -> Dict[str, Any]:
    """Resolve ENS name to address and metadata"""
    try:
        # Normalize name
        name = name.lower().strip()
        if not name.endswith('.eth'):
            name = name + '.eth'
        
        # Get namehash
        node = name_to_node(name)
        
        # Get registry
        registry = w3.eth.contract(
            address=Web3.to_checksum_address(ENS_REGISTRY_ADDRESS),
            abi=ENS_REGISTRY_ABI
        )
        
        # Get resolver address
        try:
            resolver_address = registry.functions.resolver(node).call()
            if resolver_address == "0x0000000000000000000000000000000000000000":
                return {
                    "success": False,
                    "error": "validation_error",
                    "message": f"ENS name not registered: {name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": "validation_error",
                "message": f"ENS name not found: {name}"
            }
        
        # Get owner
        try:
            owner = registry.functions.owner(node).call()
        except:
            owner = None
        
        # Get address from resolver
        resolver = w3.eth.contract(
            address=Web3.to_checksum_address(resolver_address),
            abi=ENS_RESOLVER_ABI
        )
        
        try:
            address = resolver.functions.addr(node).call()
            if not address or address == "0x0000000000000000000000000000000000000000":
                address = None
        except:
            address = None
        
        # Get text records
        text_records = {}
        for key in ["avatar", "email", "twitter", "github", "discord", "url", "description"]:
            try:
                value = resolver.functions.text(node, key).call()
                if value:
                    text_records[key] = value
            except:
                pass
        
        # Get current block for metadata
        block = w3.eth.get_block('latest')
        block_number = block['number']
        timestamp = block['timestamp']
        now = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        return {
            "success": True,
            "name": name,
            "node": node,
            "address": address,
            "owner": owner,
            "resolver": resolver_address,
            "text_records": text_records,
            "block_number": block_number,
            "rpc_used": RPC_URL,
            "timestamp": now.isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": "system_error",
            "message": str(e)
        }

def reverse_resolve_address(w3, address: str) -> Dict[str, Any]:
    """Reverse resolve address to ENS name"""
    try:
        # Validate and normalize address
        if not address.startswith('0x'):
            address = '0x' + address
        if len(address) != 42:
            return {
                "success": False,
                "error": "validation_error",
                "message": "Invalid Ethereum address format"
            }
        
        address = Web3.to_checksum_address(address)
        
        # Build reverse name (address.reverse)
        reverse_node = name_to_node(address[2:].lower() + '.addr.reverse')
        
        # Get registry
        registry = w3.eth.contract(
            address=Web3.to_checksum_address(ENS_REGISTRY_ADDRESS),
            abi=ENS_REGISTRY_ABI
        )
        
        # Get resolver
        try:
            resolver_address = registry.functions.resolver(reverse_node).call()
            if resolver_address == "0x0000000000000000000000000000000000000000":
                return {
                    "success": True,
                    "address": address,
                    "name": None,
                    "message": "No reverse ENS name registered"
                }
        except:
            return {
                "success": True,
                "address": address,
                "name": None,
                "message": "No reverse ENS name registered"
            }
        
        # Get name from resolver
        resolver = w3.eth.contract(
            address=Web3.to_checksum_address(resolver_address),
            abi=ENS_RESOLVER_ABI
        )
        
        try:
            name = resolver.functions.name(reverse_node).call()
            if not name:
                return {
                    "success": True,
                    "address": address,
                    "name": None,
                    "message": "No reverse ENS name registered"
                }
        except:
            return {
                "success": True,
                "address": address,
                "name": None,
                "message": "No reverse ENS name registered"
            }
        
        # Verify forward resolution matches
        try:
            forward_result = resolve_ens_name(w3, name)
            if forward_result.get("success") and forward_result.get("address"):
                if forward_result["address"].lower() == address.lower():
                    # Get current block for metadata
                    block = w3.eth.get_block('latest')
                    block_number = block['number']
                    timestamp = block['timestamp']
                    now = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    
                    return {
                        "success": True,
                        "address": address,
                        "name": name,
                        "verified": True,
                        "block_number": block_number,
                        "rpc_used": RPC_URL,
                        "timestamp": now.isoformat()
                    }
        except:
            pass
        
        return {
            "success": True,
            "address": address,
            "name": name,
            "verified": False,
            "message": "Reverse name found but forward resolution does not match"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": "system_error",
            "message": str(e)
        }

def main():
    try:
        if Web3 is None:
            print(json.dumps({
                "success": False,
                "error": "dependency_error",
                "message": "web3.py not installed. Install with: pip install web3"
            }))
            return
        
        input_data = json.loads(sys.stdin.read())
        
        # Get parameters
        name = input_data.get("name")
        address = input_data.get("address")
        action = input_data.get("action", "resolve")
        
        # Validate parameters
        if not name and not address:
            print(json.dumps({
                "success": False,
                "error": "validation_error",
                "message": "Either 'name' or 'address' parameter is required"
            }))
            return
        
        # Connect to blockchain
        try:
            w3 = get_web3_client()
        except Exception as e:
            print(json.dumps({
                "success": False,
                "error": "connection_error",
                "message": str(e)
            }))
            return
        
        # Process request
        if name:
            # Resolve ENS name
            result = resolve_ens_name(w3, name)
        elif address:
            # Reverse resolve address
            result = reverse_resolve_address(w3, address)
        
        print(json.dumps(result, indent=2))
    
    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "system_error",
            "message": "Invalid JSON input"
        }))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": "system_error",
            "message": str(e)
        }))

if __name__ == "__main__":
    main()
