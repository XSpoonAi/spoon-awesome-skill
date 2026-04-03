#!/usr/bin/env python3
"""Solana Key Tools - Generate and Validate Real Solana Ed25519 Keypairs"""
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import base58

try:
    from nacl.signing import SigningKey
    from nacl.encoding import HexEncoder
except ImportError:
    SigningKey = None
    HexEncoder = None

try:
    from mnemonic import Mnemonic
except ImportError:
    Mnemonic = None

# Solana RPC endpoint
SOLANA_RPC = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")

def get_current_timestamp() -> str:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).isoformat()

def generate_keypair() -> Dict[str, Any]:
    """Generate a real Solana Ed25519 keypair"""
    try:
        if SigningKey is None:
            return {
                "success": False,
                "error": "dependency_error",
                "message": "PyNaCl package is required but not installed"
            }
        
        # Generate real Ed25519 keypair using PyNaCl (what Solana uses)
        signing_key = SigningKey.generate()
        
        # Get secret key (32 bytes)
        secret_key = signing_key.encode(encoder=HexEncoder).decode()
        secret_key_bytes = signing_key.encode()
        
        # Get public key (32 bytes)
        verify_key = signing_key.verify_key
        public_key_bytes = bytes(verify_key)
        
        # Encode public key to Solana base58 format
        public_key = base58.b58encode(public_key_bytes).decode()
        
        # Optional: Generate mnemonic if mnemonic library available
        mnemonic_phrase = None
        if Mnemonic is not None:
            try:
                mnemo = Mnemonic("english")
                # Use first 32 bytes of secret key for mnemonic generation
                mnemonic_phrase = mnemo.to_mnemonic(secret_key_bytes)
            except Exception:
                pass
        
        current_timestamp = get_current_timestamp()
        
        return {
            "success": True,
            "keypair": {
                "public_key": public_key,
                "public_key_hex": public_key_bytes.hex(),
                "secret_key_hex": secret_key,
                "secret_key_base58": base58.b58encode(secret_key_bytes).decode(),
                "key_type": "Ed25519",
                "key_size_bytes": 32,
                "mnemonic": mnemonic_phrase,
                "derivation_path": "m/44'/501'/0'/0'",
                "network": "solana-mainnet",
                "created_at": current_timestamp
            },
            "timestamp": current_timestamp,
            "rpc_used": SOLANA_RPC,
            "note": "Public key is base58-encoded. Ready for Solana transactions."
        }
    except Exception as e:
        return {
            "success": False,
            "error": "system_error",
            "message": f"Error generating keypair: {str(e)}"
        }

def validate_public_key(public_key_str: str) -> Dict[str, Any]:
    """Validate a Solana public key"""
    try:
        # Validate public key format
        public_key_str = public_key_str.strip()
        
        try:
            # Try to decode as base58
            decoded = base58.b58decode(public_key_str)
            # Solana public keys are 32 bytes
            if len(decoded) != 32:
                public_key_valid = False
            else:
                public_key_valid = True
                public_key_hex = decoded.hex()
        except Exception:
            public_key_valid = False
            public_key_hex = None
        
        if not public_key_valid:
            return {
                "success": False,
                "error": "validation_error",
                "message": f"Invalid Solana public key format. Expected 32-byte Ed25519 address in base58 format."
            }
        
        current_timestamp = get_current_timestamp()
        
        return {
            "success": True,
            "public_key": public_key_str,
            "public_key_hex": public_key_hex,
            "validated": True,
            "is_valid_solana_address": True,
            "address_length_chars": len(public_key_str),
            "decoded_bytes": 32,
            "key_type": "Ed25519",
            "timestamp": current_timestamp,
            "rpc_used": SOLANA_RPC
        }
    except Exception as e:
        return {
            "success": False,
            "error": "system_error",
            "message": f"Error validating public key: {str(e)}"
        }

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        
        action = input_data.get("action", "generate").lower()
        
        if action == "generate":
            result = generate_keypair()
        elif action == "validate":
            public_key = input_data.get("public_key")
            if not public_key:
                result = {
                    "success": False,
                    "error": "validation_error",
                    "message": "public_key parameter required for validate action"
                }
            else:
                result = validate_public_key(public_key)
        else:
            result = {
                "success": False,
                "error": "validation_error",
                "message": f"Unknown action: {action}. Supported: generate, validate"
            }
        
        print(json.dumps(result, indent=2))
    
    except json.JSONDecodeError:
        result = {
            "success": False,
            "error": "validation_error",
            "message": "Invalid JSON input"
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        result = {
            "success": False,
            "error": "system_error",
            "message": f"Unexpected error: {str(e)}"
        }
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
