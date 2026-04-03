# Cyfrin Audit Report Template

## Report Cover
```markdown
![Cyfrin Logo]

# Security Audit Report

## [Protocol Name]

**Prepared by:** Cyfrin  
**Lead Auditor:** [Name]  
**Audit Date:** [Start Date] - [End Date]  
**Report Version:** 1.0
```

## Table of Contents
```markdown
## Table of Contents

1. [Protocol Summary](#protocol-summary)
2. [Disclaimer](#disclaimer)
3. [Risk Classification](#risk-classification)
4. [Audit Details](#audit-details)
5. [Executive Summary](#executive-summary)
6. [Findings](#findings)
```

## Protocol Summary
```markdown
## Protocol Summary

[Protocol Name] is a [brief description of what the protocol does].

### Key Features
- Feature 1
- Feature 2
- Feature 3

### Architecture
[Brief description of the architecture and how contracts interact]
```

## Risk Classification (Cyfrin Style)
```markdown
## Risk Classification

| Severity | Impact: High | Impact: Medium | Impact: Low |
|----------|-------------|----------------|-------------|
| **Likelihood: High** | Critical | High | Medium |
| **Likelihood: Medium** | High | Medium | Low |
| **Likelihood: Low** | Medium | Low | Low |

### Impact
- **High** - Loss of funds, permanent protocol disruption
- **Medium** - Partial loss, temporary disruption, value leakage
- **Low** - Minimal impact, informational

### Likelihood
- **High** - Easy to exploit, no special conditions
- **Medium** - Requires specific conditions or timing
- **Low** - Difficult to exploit, edge cases
```

## Audit Details
```markdown
## Audit Details

### Scope
| File | SLOC |
|------|------|
| `src/Contract1.sol` | 200 |
| `src/Contract2.sol` | 150 |
| **Total** | **350** |

### Commit Hash
`abc123def456`

### Methods
- Manual Code Review
- Static Analysis (Slither, Aderyn)
- Dynamic Testing (Foundry)

### Out of Scope
- External dependencies
- Frontend code
- Deployment scripts
```

## Finding Template (Cyfrin Style)
```markdown
### [S-#] Title

**Severity:** Critical / High / Medium / Low / Informational / Gas

**Description:**
[Detailed description of the vulnerability]

**Impact:**
[What is the impact of this vulnerability]

**Proof of Concept:**
```solidity
function test_vulnerability() public {
    // PoC code
}
```

**Recommended Mitigation:**
```solidity
// Mitigation code
```

**[Protocol Team Response]:**
[Fixed / Acknowledged / Disputed]
```

## Executive Summary Template
```markdown
## Executive Summary

### Issues Found

| Severity | Count | Fixed | Acknowledged |
|----------|-------|-------|--------------|
| Critical | 0 | 0 | 0 |
| High | 2 | 2 | 0 |
| Medium | 3 | 2 | 1 |
| Low | 5 | 3 | 2 |
| Gas | 4 | 4 | 0 |
| **Total** | **14** | **11** | **3** |

### Audit Timeline
- **Day 1-2:** Initial review, architecture understanding
- **Day 3-5:** Deep dive into core functionality
- **Day 6-7:** Edge cases, attack vectors
- **Day 8:** Report writing, PoC development
```

## Disclaimer
```markdown
## Disclaimer

The Cyfrin team makes all effort to find as many vulnerabilities in the code in the given time period, but holds no responsibilities for the findings provided in this document. A security audit by the team is not an endorsement of the underlying business or product. The audit was time-boxed and the review of the code was solely on the security aspects of the Solidity implementation of the contracts.
```
