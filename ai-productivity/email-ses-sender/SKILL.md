---
name: email-ses-sender
track: ai-productivity
version: 0.1.0
summary: Send templated emails via AWS SES
---

## Description

Send templated emails via AWS SES (Simple Email Service). Supports email templates, variables, and sandbox testing mode.

## Inputs

```json
{
  "to": "Recipient email",
  "subject": "Email subject",
  "template": "Template name",
  "variables": {}
}
```

## Outputs

```json
{
  "ok": true,
  "data": {
    "message_id": "Email message ID",
    "status": "sent"
  }
}
```

## Usage

### Demo Mode
```bash
python scripts/main.py --demo
```

### Send Email
```bash
echo '{"to":"user@example.com","subject":"Hello","template":"welcome"}' | python3 scripts/main.py
```

## Examples

### Example 1: Send Welcome Email
```bash
$ echo '{"to":"user@example.com","subject":"Welcome!","template":"welcome","variables":{"name":"John"}}' | python3 scripts/main.py
{
  "ok": true,
  "data": {
    "message_id": "0000014a-aee4-4a01-a640-a8f7f5bd5e7e-000000",
    "status": "sent"
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
    "to": "Invalid email address"
  }
}
```
