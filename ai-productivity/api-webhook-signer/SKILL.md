---
name: api-webhook-signer
track: ai-productivity
version: 0.1.0
summary: Generate/verify signed webhooks with HMAC-SHA256 and retry queue with exponential backoff
---

## Description

Generate HMAC-SHA256 signatures for webhook payloads and verify incoming webhook signatures. Includes retry queue generation with configurable exponential backoff for reliable webhook delivery.

## Inputs

JSON parameters via `--params`:

```json
{
  "action": "sign|verify",
  "payload": {"event": "user.created", "user_id": 123},
  "secret": "your_secret_key",
  "signature": "signature_to_verify (for verify action)",
  "retry_config": {
    "max_attempts": 3,
    "base_delay": 1,
    "backoff_multiplier": 2
  }
}
```

## Outputs

JSON to stdout:

**Sign action:**
```json
{
  "ok": true,
  "data": {
    "action": "sign",
    "signature": "hmac_sha256_hex",
    "payload": {...},
    "retry_queue": [
      {"attempt": 1, "delay_seconds": 1, "next_retry": "2026-02-06T10:00:01Z"}
    ]
  }
}
```

**Verify action:**
```json
{
  "ok": true,
  "data": {
    "action": "verify",
    "valid": true,
    "payload": {...}
  }
}
```

## Usage

```bash
# Demo mode
python scripts/main.py --demo

# Sign a webhook
python scripts/main.py --params '{"action":"sign","payload":{"event":"test"},"secret":"key123"}'

# Verify a webhook
python scripts/main.py --params '{"action":"verify","payload":{"event":"test"},"secret":"key123","signature":"abc..."}'

# Sign with retry queue
python scripts/main.py --params '{"action":"sign","payload":{"event":"test"},"secret":"key123","retry_config":{"max_attempts":5}}'
```
