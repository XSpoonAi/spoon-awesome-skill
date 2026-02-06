# Contract Event Tail

Monitor and retrieve blockchain event logs from smart contracts in real-time.

## Features
- Multi-chain event monitoring (Ethereum, Polygon, Arbitrum, Optimism)
- Event filtering and retrieval
- Historical event lookup
- Decoded event data
- Block range queries

## Usage

```bash
echo '{
  "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  "from_block": 17000000,
  "to_block": 17000100,
  "chain": "ethereum"
}' | python3 scripts/main.py
```

## Parameters
- `contract_address` (required): Smart contract address
- `from_block` (required): Starting block number
- `to_block` (required): Ending block number
- `chain` (optional): Blockchain (ethereum, polygon, arbitrum, optimism)

## Response
Returns event logs with transaction hash, block number, and decoded data.
