#!/usr/bin/env python3
"""ERC20 Allowance Manager - Real blockchain RPC implementation (NO SIMULATOR)"""
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum

try:
    from web3 import Web3
    from web3.exceptions import BlockNotFound, InvalidAddress
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "dependency_error",
        "message": "web3.py required. Install with: pip install web3"
    }))
    sys.exit(1)

class ApprovalStrategy(Enum):
    """Different ERC20 approval strategies"""
    UNLIMITED = "unlimited"
    EXACT = "exact"

# ERC20 ABI - Core functions only
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Known spenders for identification
KNOWN_SPENDERS = {
    "0x1111111254fb6c44bac0bed2854e76f90643097d": "1inch Router",
    "0x68b3465833fb72b5a828cceeb955439b22b36987": "Uniswap V3 SwapRouter02",
    "0xe592427a0aeee92de3edee1f18e0157c05861564": "Uniswap V3 SwapRouter",
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2 Router",
    "0xa5e0829caced8ffdd4de3c43696c57f7d7a07a97": "QuickSwap Router",
    "0x00000000000001ad428e4906ae43880f4014ed4d": "OpenSea Seaport",
    "0xe592427a0aeee92de3edee1f18e0157c05df0392": "Permit2",
    "0xe592427a0aeee92de3edee1f18e0157c05861564": "Uniswap V2 Router02",
}

def get_rpc_url() -> str:
    """Get RPC URL from environment or raise error"""
    rpc_url = os.getenv("ETH_RPC_URL") or os.getenv("WEB3_PROVIDER_URI")
    if not rpc_url:
        raise ValueError(
            "RPC URL required. Set ETH_RPC_URL or WEB3_PROVIDER_URI environment variable. "
            "Example: ETH_RPC_URL='https://eth.llamarpc.com'"
        )
    return rpc_url

def validate_address(address: str) -> bool:
    """Validate Ethereum address format"""
    try:
        Web3.to_checksum_address(address)
        return True
    except (InvalidAddress, ValueError):
        return False

def get_spender_name(spender_address: str) -> str:
    """Get friendly name for known spenders"""
    return KNOWN_SPENDERS.get(spender_address.lower(), "Unknown Contract")

def format_amount(amount: int, decimals: int) -> float:
    """Convert raw amount to decimal format"""
    return amount / (10 ** decimals)

def parse_amount(amount: str, decimals: int) -> int:
    """Convert decimal amount to raw format"""
    return int(float(amount) * (10 ** decimals))

def check_allowance(owner: str, spender: str, token: str, rpc_url: str) -> Dict:
    """Check ERC20 allowance using real blockchain RPC call"""
    
    # Validate inputs
    if not validate_address(owner):
        raise ValueError(f"Invalid owner address: {owner}")
    if not validate_address(spender):
        raise ValueError(f"Invalid spender address: {spender}")
    if not validate_address(token):
        raise ValueError(f"Invalid token address: {token}")
    
    # Connect to blockchain
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise ConnectionError(f"Cannot connect to RPC endpoint: {rpc_url}")
    except Exception as e:
        raise ConnectionError(f"RPC connection failed: {str(e)}")
    
    # Get current block number for context
    try:
        block_number = w3.eth.block_number
    except Exception as e:
        raise RuntimeError(f"Failed to get block number: {str(e)}")
    
    # Create contract instance with checksum addresses
    owner_checksum = Web3.to_checksum_address(owner)
    spender_checksum = Web3.to_checksum_address(spender)
    token_checksum = Web3.to_checksum_address(token)
    
    try:
        contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
    except Exception as e:
        raise RuntimeError(f"Failed to create contract instance: {str(e)}")
    
    # Fetch token info
    try:
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        name = contract.functions.name().call()
        total_supply = contract.functions.totalSupply().call()
    except Exception as e:
        raise ValueError(f"Failed to fetch token info from {token}. Is this a valid ERC20 token? Error: {str(e)}")
    
    # Fetch real allowance from blockchain
    try:
        raw_allowance = contract.functions.allowance(owner_checksum, spender_checksum).call()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch allowance: {str(e)}")
    
    # Fetch owner's balance for context
    try:
        owner_balance = contract.functions.balanceOf(owner_checksum).call()
    except Exception as e:
        owner_balance = 0
    
    formatted_allowance = format_amount(raw_allowance, decimals)
    owner_balance_formatted = format_amount(owner_balance, decimals)
    max_uint256 = 2**256 - 1
    
    return {
        "success": True,
        "allowance": {
            "owner": owner,
            "spender": spender,
            "spender_name": get_spender_name(spender),
            "token": {
                "address": token,
                "symbol": symbol,
                "name": name,
                "decimals": decimals,
                "total_supply": str(total_supply)
            },
            "owner_balance": round(owner_balance_formatted, decimals),
            "raw_allowance": str(raw_allowance),
            "formatted_allowance": round(formatted_allowance, decimals),
            "is_unlimited": raw_allowance == max_uint256,
            "is_exhausted": raw_allowance > 0 and raw_allowance < 10**(decimals-1),
            "approval_risk": "high" if raw_allowance == max_uint256 else "low"
        },
        "blockchain": {
            "rpc_used": rpc_url.split('/')[-1] if '/' in rpc_url else rpc_url,
            "block_number": block_number,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }

def batch_check_allowances(owner: str, spenders: List[str], token: str, rpc_url: str) -> Dict:
    """Check allowances for multiple spenders from real blockchain"""
    
    if not validate_address(owner):
        raise ValueError(f"Invalid owner address: {owner}")
    if not validate_address(token):
        raise ValueError(f"Invalid token address: {token}")
    
    if not spenders or len(spenders) == 0:
        raise ValueError("At least one spender required")
    if len(spenders) > 50:
        raise ValueError("Maximum 50 spenders per batch")
    
    for spender in spenders:
        if not validate_address(spender):
            raise ValueError(f"Invalid spender address: {spender}")
    
    # Connect to blockchain
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise ConnectionError(f"Cannot connect to RPC: {rpc_url}")
    except Exception as e:
        raise ConnectionError(f"RPC connection failed: {str(e)}")
    
    # Get token info
    token_checksum = Web3.to_checksum_address(token)
    try:
        contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        name = contract.functions.name().call()
        block_number = w3.eth.block_number
    except Exception as e:
        raise ValueError(f"Failed to fetch token info: {str(e)}")
    
    # Check each spender
    allowances = []
    owner_checksum = Web3.to_checksum_address(owner)
    
    for spender in spenders:
        spender_checksum = Web3.to_checksum_address(spender)
        try:
            raw_allowance = contract.functions.allowance(owner_checksum, spender_checksum).call()
            formatted_allowance = format_amount(raw_allowance, decimals)
            
            allowances.append({
                "spender": spender,
                "spender_name": get_spender_name(spender),
                "raw_allowance": str(raw_allowance),
                "formatted_allowance": round(formatted_allowance, decimals),
                "is_unlimited": raw_allowance == (2**256 - 1),
                "approval_risk": "high" if raw_allowance == (2**256 - 1) else "low"
            })
        except Exception as e:
            raise RuntimeError(f"Failed to check allowance for spender {spender}: {str(e)}")
    
    return {
        "success": True,
        "batch_result": {
            "owner": owner,
            "token": {
                "address": token,
                "symbol": symbol,
                "name": name,
                "decimals": decimals
            },
            "spender_count": len(spenders),
            "allowances": allowances,
            "unlimited_allowances": sum(1 for a in allowances if a["is_unlimited"]),
            "summary": f"{len(spenders)} spenders checked, {sum(1 for a in allowances if a['is_unlimited'])} with unlimited access"
        },
        "blockchain": {
            "rpc_used": rpc_url.split('/')[-1] if '/' in rpc_url else rpc_url,
            "block_number": block_number,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }

def encode_approval(owner: str, spender: str, token: str, amount: Optional[str], strategy: str) -> Dict:
    """Encode an approval transaction (for simulation/broadcasting)"""
    
    if not validate_address(owner):
        raise ValueError(f"Invalid owner address: {owner}")
    if not validate_address(spender):
        raise ValueError(f"Invalid spender address: {spender}")
    if not validate_address(token):
        raise ValueError(f"Invalid token address: {token}")
    
    # Get RPC to fetch token decimals
    rpc_url = os.getenv("ETH_RPC_URL") or os.getenv("WEB3_PROVIDER_URI")
    
    token_checksum = Web3.to_checksum_address(token)
    decimals = 18  # Default
    
    if rpc_url:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
            decimals = contract.functions.decimals().call()
            symbol = contract.functions.symbol().call()
            name = contract.functions.name().call()
        except:
            raise ValueError(f"Cannot fetch token decimals from {token}")
    else:
        raise ValueError("RPC URL required to encode approval")
    
    # Determine amount
    if strategy == ApprovalStrategy.UNLIMITED.value:
        raw_amount = 2**256 - 1
        formatted_amount = "unlimited"
    elif strategy == ApprovalStrategy.EXACT.value:
        if not amount:
            raise ValueError("Amount required for exact strategy")
        raw_amount = parse_amount(amount, decimals)
        formatted_amount = f"{amount} {symbol}"
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    # Encode approve function call
    spender_checksum = Web3.to_checksum_address(spender)
    try:
        contract = w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
        # Encode the approve function call
        encoded_data = contract.encodeABI(fn_name="approve", args=[spender_checksum, raw_amount])
    except Exception as e:
        raise RuntimeError(f"Failed to encode approval: {str(e)}")
    
    return {
        "success": True,
        "approval_encoding": {
            "owner": owner,
            "spender": spender,
            "spender_name": get_spender_name(spender),
            "token": {
                "address": token,
                "symbol": symbol,
                "name": name,
                "decimals": decimals
            },
            "strategy": strategy,
            "raw_amount": str(raw_amount),
            "formatted_amount": formatted_amount,
            "transaction": {
                "to": token,
                "function": "approve(address,uint256)",
                "encoded_data": encoded_data,
                "value": "0",
                "from": owner
            }
        }
    }

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        
        action = input_data.get("action", "check")
        owner = input_data.get("owner")
        spender = input_data.get("spender")
        token = input_data.get("token")
        rpc_url = input_data.get("rpc_url") or get_rpc_url()
        
        # Validate required fields
        if not owner or not token:
            print(json.dumps({
                "success": False,
                "error": "validation_error",
                "message": "owner and token are required"
            }))
            return
        
        if action == "check":
            if not spender:
                print(json.dumps({
                    "success": False,
                    "error": "validation_error",
                    "message": "spender required for check action"
                }))
                return
            result = check_allowance(owner, spender, token, rpc_url)
        
        elif action == "batch_check":
            spenders = input_data.get("spenders", [])
            result = batch_check_allowances(owner, spenders, token, rpc_url)
        
        elif action == "encode_approval":
            if not spender:
                print(json.dumps({
                    "success": False,
                    "error": "validation_error",
                    "message": "spender required for encode_approval action"
                }))
                return
            amount = input_data.get("amount")
            strategy = input_data.get("strategy", "exact")
            result = encode_approval(owner, spender, token, amount, strategy)
        
        else:
            print(json.dumps({
                "success": False,
                "error": "validation_error",
                "message": f"Unknown action: {action}"
            }))
            return
        
        print(json.dumps(result, indent=2))
    
    except ValueError as e:
        print(json.dumps({
            "success": False,
            "error": "validation_error",
            "message": str(e)
        }))
    except ConnectionError as e:
        print(json.dumps({
            "success": False,
            "error": "connection_error",
            "message": str(e)
        }))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": "system_error",
            "message": str(e)
        }))

if __name__ == "__main__":
    main()
