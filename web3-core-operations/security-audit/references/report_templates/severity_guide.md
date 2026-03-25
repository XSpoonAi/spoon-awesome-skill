# Severity Rating Guide

## Universal Severity Matrix

```
                    │  Low Impact  │ Medium Impact │  High Impact  │
────────────────────┼──────────────┼───────────────┼───────────────│
High Likelihood     │    Medium    │     High      │   Critical    │
Medium Likelihood   │     Low      │    Medium     │     High      │
Low Likelihood      │ Informational│     Low       │    Medium     │
```

## Impact Definitions

### High Impact
- Direct loss of user funds
- Protocol insolvency
- Permanent DoS of critical functions
- Unauthorized minting/burning of tokens
- Complete access control bypass

### Medium Impact
- Temporary freezing of funds (recoverable)
- Partial loss under specific conditions
- Temporary DoS
- Theft of yield/fees (not principal)
- Griefing with moderate cost to attacker

### Low Impact
- Informational leakage
- Minor gas inefficiencies
- Edge cases with minimal practical impact
- Best practice violations

## Likelihood Definitions

### High Likelihood
- No special conditions required
- Profitable for attacker
- Can be executed by anyone
- Automated exploitation possible

### Medium Likelihood
- Requires specific timing or state
- Requires moderate capital
- Depends on external conditions
- Requires insider knowledge

### Low Likelihood
- Requires extreme conditions
- Unprofitable attack
- Requires trusted party to be malicious
- Theoretical with no practical path

## Platform-Specific Guidelines

### Code4rena
| Severity | Criteria |
|----------|----------|
| High | Direct fund loss, no hypotheticals |
| Medium | Conditional loss, function disruption |
| Low | Edge cases, informational |
| Gas | Optimization only |

### Sherlock
| Severity | Criteria |
|----------|----------|
| High | Definite loss without external factors |
| Medium | Loss with conditions, griefing, DoS |
| Low | Informational, best practices |

### Cyfrin
Uses the 3x3 matrix (Impact × Likelihood)

### Immunefi
| Severity | Bounty Range |
|----------|--------------|
| Critical | $50k - $1M+ |
| High | $10k - $50k |
| Medium | $1k - $10k |
| Low | $100 - $1k |

## Common Severity Mistakes

### Over-Rating
- Theoretical attacks without practical path → Lower severity
- Admin-only issues → Usually Low/Info
- Requires trusted party malicious → Lower severity
- No profit motive for attacker → Lower severity

### Under-Rating
- "Unlikely" but devastating → Still High if impact is Critical
- Chained vulnerabilities → Rate the final impact
- MEV/frontrunning with profit → Usually Medium+

## Quick Reference

| Issue Type | Typical Severity |
|------------|------------------|
| Reentrancy with fund loss | Critical/High |
| Oracle manipulation | High |
| Access control bypass | High |
| Flash loan attack possible | High/Medium |
| Integer overflow | Medium/High |
| DoS (temporary) | Medium |
| DoS (permanent) | High |
| Missing input validation | Low/Medium |
| Centralization risk | Medium/Low |
| Gas optimization | Gas/Info |
| Code quality | Info |
