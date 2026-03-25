# Generic Audit Report Template

## Report Structure
```markdown
# Security Audit Report

**Protocol:** [Name]  
**Auditor:** [Name/Firm]  
**Date:** [Date]  
**Commit:** [hash]  
**Scope:** [Brief description]
```

## Executive Summary
```markdown
## Executive Summary

### Overview
[1-2 paragraph description of the protocol and audit scope]

### Key Findings
- **Critical:** X issues
- **High:** X issues  
- **Medium:** X issues
- **Low:** X issues
- **Informational:** X issues

### Recommendations
1. [Top priority recommendation]
2. [Second priority]
3. [Third priority]
```

## Finding Template
```markdown
## [ID] Finding Title

| Field | Value |
|-------|-------|
| Severity | Critical/High/Medium/Low/Info |
| Status | Open/Fixed/Acknowledged |
| File | `Contract.sol` |
| Lines | L100-L120 |

### Description
[What is the issue]

### Impact
[What damage can occur]

### Proof of Concept
```solidity
// PoC code
```

### Recommendation
```solidity
// Fix code
```

### Team Response
[Protocol team's response]
```

## Severity Matrix
```
              │ Low Impact │ Medium Impact │ High Impact │
──────────────┼────────────┼───────────────┼─────────────│
High Likelihood   │   Medium   │     High      │   Critical  │
Medium Likelihood │    Low     │    Medium     │    High     │
Low Likelihood    │    Info    │     Low       │   Medium    │
```

## Appendix Sections
```markdown
## Appendix A: Scope

| Contract | SLOC | Description |
|----------|------|-------------|
| ... | ... | ... |

## Appendix B: Methodology

### Tools Used
- Manual review
- Static analysis (Slither, Aderyn)
- Dynamic testing (Foundry)
- Fuzzing (Echidna)

### Review Process
1. Architecture review
2. Code walkthrough
3. Attack vector identification
4. PoC development
5. Report writing

## Appendix C: Disclaimer

This audit does not guarantee the absence of vulnerabilities. It represents a point-in-time assessment based on the provided code.
```
