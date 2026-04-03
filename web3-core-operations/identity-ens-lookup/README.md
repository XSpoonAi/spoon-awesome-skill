# Identity ENS Lookup

Resolve Ethereum Name Service (ENS) names and manage records.

## Features
- Name to address resolution
- Reverse name lookup
- Avatar resolution
- Text record lookup
- Multi-address support

## Usage

```bash
echo '{
  "name": "vitalik.eth"
}' | python3 scripts/main.py
```

## Response
Returns resolved address, owner, avatar, and text records.
