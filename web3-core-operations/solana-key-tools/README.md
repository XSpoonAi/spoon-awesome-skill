# Solana Key Tools

Generate and validate real Solana Ed25519 keypairs using cryptographic libraries. All keypairs are Solana-compatible with optional BIP39 mnemonic phrases.

## Features

- **Real Ed25519 Keypairs**: Cryptographically secure generation using PyNaCl/libsodium
- **Solana Compatible**: Base58-encoded addresses ready for immediate use
- **Mnemonic Support**: BIP39 24-word seed phrases for keypair recovery
- **Address Validation**: Validate Solana public keys (44-character base58 addresses)
- **Complete Key Details**: Public/secret keys in both hex and base58 formats
- **Blockchain Metadata**: RPC endpoint and timestamp with every response

## Installation

```bash
cd solana-key-tools
pip install PyNaCl mnemonic base58  # Dependencies
```

## Usage

### Generate Real Keypair

```bash
echo '{"action": "generate"}' | python3 scripts/main.py
```

### Validate Solana Address

```bash
echo '{
  "action": "validate",
  "public_key": "5PwVmDs2S81FF6raBTDvAYQNwVp9otA746uGkxNbPFgV"
}' | python3 scripts/main.py
```

## Response Format

### Generate Response

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
    "mnemonic": "tragic crack flash market burger sausage drink gun scrub science thank chunk repair notice culture powder inspire story section mistake room income bachelor hurdle",
    "derivation_path": "m/44'/501'/0'/0'",
    "network": "solana-mainnet"
  },
  "timestamp": "2026-02-06T16:16:53.657135+00:00",
  "rpc_used": "https://api.mainnet-beta.solana.com"
}
```

### Validate Response

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

## Keypair Details

### Public Key (Address)
- **Format**: Base58 string (44 characters)
- **Bytes**: 32 bytes (256 bits)
- **Usage**: Receive funds, transactions
- **Example**: `5PwVmDs2S81FF6raBTDvAYQNwVp9otA746uGkxNbPFgV`

### Secret Key (Private Key)
- **Format**: Ed25519 private key
- **Stored As**: Hex string or Base58
- **Security**: NEVER share or expose
- **Usage**: Signing transactions

### Mnemonic Phrase
- **Standard**: BIP39
- **Length**: 24 words
- **Purpose**: Keypair recovery
- **Security**: Backup safely, equivalent to private key

## Key Cryptography

### Ed25519 Algorithm
- **Type**: Edwards-Curve Digital Signature Algorithm
- **Security Level**: 128 bits (256-bit keys)
- **Performance**: Fast signature generation and verification
- **Compatibility**: Native Solana keypair format

### Base58 Encoding
- **Purpose**: Human-readable address format
- **Length**: 44 characters for Solana addresses
- **Standard**: Bitcoin base58 (excludes 0, O, I, l)

## Actions

| Action | Purpose | Parameters |
|--------|---------|------------|
| `generate` | Create new keypair | None required |
| `validate` | Check if address is valid | `public_key` (required) |

## Error Handling

- **validation_error**: Invalid public key format or missing parameters
- **system_error**: Unexpected error in key generation/validation
- **dependency_error**: Missing PyNaCl or other required packages

## Security Notes

⚠️ **Important**:
- Never expose secret keys in logs or error messages
- Store mnemonics in secure location (hardware wallet, password manager)
- Use keypairs only for testing/development unless on prod with proper security
- Always back up mnemonic phrases immediately

## Testing

All keys are generated using cryptographically secure randomness:
- Public keys and addresses are verifiable
- Mnemonics can be imported into Solana wallets
- Keypairs are immediately ready for transaction signing

## Next Steps: Using Keypairs

To sign and send transactions with generated keypairs:

```python
# Example: Sign transaction with keypair
from nacl.signing import SigningKey
from base58 import b58decode

secret_key_hex = "e6e63961c411eb7f50c33fc1d81f7f145b692dcd..."
signing_key = SigningKey(bytes.fromhex(secret_key_hex))

# Sign message/transaction
message = b"Hello Solana"
signature = signing_key.sign(message)
```

All generated keypairs are compatible with Solana CLI and Client libraries.
