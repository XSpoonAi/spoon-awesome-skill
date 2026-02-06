---
name: solana-key-tools
track: web3-core-operations
version: 0.1.0
summary: Generate Real Solana Ed25519 Keypairs with Validation
---

## Description

Generate and validate real Solana Ed25519 keypairs using cryptographic libraries. Keypairs are compatible with Solana blockchain, include optional mnemonic phrases, and support public key validation.

## Key Features

- ✅ **Real Ed25519 Keypairs**: Cryptographically secure keypair generation
- ✅ **Solana Compatible**: Base58-encoded addresses compatible with Solana network
- ✅ **Mnemonic Support**: BIP39 mnemonic phrase generation
- ✅ **Address Validation**: Validate Solana public keys
- ✅ **Full Key Details**: Public key, secret key, hex, base58, mnemonic
- ✅ **Blockchain Metadata**: RPC endpoint and timestamp proof

## Inputs

### Generate Action
```json
{
  "action": "generate"
}
```

### Validate Action
```json
{
  "action": "validate",
  "public_key": "5PwVmDs2S81FF6raBTDvAYQNwVp9otA746uGkxNbPFgV"
}
```

## Outputs

### Generate Output
```json
{
  "success": true,
  "keypair": {
    "public_key": "5PwVmDs2S81FF6raBTDvAYQNwVp9otA746uGkxNbPFgV",
    "public_key_hex": "414f24eba0bbe03885b0d8dbacb12a5b53e302f5796...",
    "secret_key_hex": "e6e63961c411eb7f50c33fc1d81f7f145b692dcd...",
    "secret_key_base58": "GYLP9g52EGrvuNCLKy19qjUKojfuqEuY1uBbiH5XDnKc",
    "key_type": "Ed25519",
    "key_size_bytes": 32,
    "mnemonic": "tragic crack flash market burger sausage...",
    "derivation_path": "m/44'/501'/0'/0'",
    "network": "solana-mainnet",
    "created_at": "2026-02-06T16:16:53.657135+00:00"
  },
  "timestamp": "2026-02-06T16:16:53.657135+00:00",
  "rpc_used": "https://api.mainnet-beta.solana.com",
  "note": "Public key is base58-encoded. Ready for Solana transactions."
}
```

### Validate Output
```json
{
  "success": true,
  "public_key": "5PwVmDs2S81FF6raBTDvAYQNwVp9otA746uGkxNbPFgV",
  "public_key_hex": "414f24eba0bbe03885b0d8dbacb12a5b53e302f57968...",
  "validated": true,
  "is_valid_solana_address": true,
  "address_length_chars": 44,
  "decoded_bytes": 32,
  "key_type": "Ed25519",
  "timestamp": "2026-02-06T16:16:57.586754+00:00",
  "rpc_used": "https://api.mainnet-beta.solana.com"
}
```

## Usage

### Generate Keypair
```bash
echo '{"action": "generate"}' | python3 scripts/main.py
```

### Validate Public Key
```bash
echo '{"action": "validate", "public_key": "5PwVmDs2S81FF6raBTDvAYQNwVp9otA746uGkxNbPFgV"}' | python3 scripts/main.py
```

## Cryptographic Details

### Key Generation
- **Algorithm**: Ed25519 (Edwards-curve Digital Signature Algorithm)
- **Key Size**: 32 bytes (256 bits)
- **Randomness**: Cryptographically secure random from OS
- **Library**: PyNaCl (libsodium)

### Public Key Encoding
- **Format**: Base58 (no checksum version)
- **Length**: 44 base58 characters
- **Compatibility**: Direct use in Solana transactions

### Mnemonic Generation
- **Standard**: BIP39
- **Language**: English
- **Wordlist**: 2048 standard English words
- **Entropy**: 256 bits (32 bytes) → 24-word phrase

## Error Handling

**Validation Error**: Invalid public key format or missing required parameters
**System Error**: Unexpected error in cryptographic operations
**Dependency Error**: Missing required Python packages

### Example 1: Generate New Keypair
```bash
$ echo '{"action": "generate"}' | python3 scripts/main.py
{
  "success": true,
  "keypair": {
    "public_key": "d7da9403d03eb30503f207e109890388145521087e48",
    "secret_key": "615666dae9d3625adaef933e4c1ed0158f657a22c2f570edcd1f7caa68e16413",
    "mnemonic": "abandon ability able ... zero zone",
    "derivation_path": "m/44'/501'/0'/0'",
    "created_at": "2026-02-06T07:20:45Z"
  }
}
```

## Error Handling

When an error occurs, the skill returns:

```json
{
  "ok": false,
  "error": "Error description",
  "details": {
    "action": "Invalid action"
  }
}
```
