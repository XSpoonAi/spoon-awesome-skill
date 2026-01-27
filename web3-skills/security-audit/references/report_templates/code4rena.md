# Code4rena Report Template

## Report Header
```markdown
# [Protocol Name] Audit Report

### Prepared by: [Auditor/Team Name]
### Date: [Date]
### Review Commit: [commit hash]
```

## Executive Summary
```markdown
## Executive Summary

[Protocol Name] engaged [Auditor] to review the security of their smart contracts. The audit was conducted over [X days] from [start date] to [end date].

### Scope
| Contract | SLOC | Purpose |
|----------|------|---------|
| Contract1.sol | 200 | Main logic |
| Contract2.sol | 150 | Token handling |

### Findings Summary
| Severity | Count |
|----------|-------|
| High | X |
| Medium | X |
| Low | X |
| Gas | X |
| Informational | X |
```

## Finding Template (Code4rena Style)
```markdown
## [H-01] Title of the vulnerability

### Severity
High

### Relevant GitHub Links
https://github.com/code-423n4/[contest]/blob/main/src/Contract.sol#L100-L120

### Summary
Brief description of the vulnerability (1-2 sentences).

### Vulnerability Detail
Detailed explanation of the vulnerability:
- What is the root cause
- How it can be exploited
- What conditions are needed

### Impact
What damage can be caused:
- Loss of funds (quantify if possible)
- Protocol disruption
- User harm

### Code Snippet
```solidity
// Vulnerable code
function withdraw(uint256 amount) external {
    // Missing access control
    token.transfer(msg.sender, amount);
}
```

### Tool Used
Manual Review / Foundry / Slither

### Recommendation
```solidity
// Fixed code
function withdraw(uint256 amount) external onlyOwner {
    token.transfer(msg.sender, amount);
}
```
```

## Severity Classification (Code4rena)

| Severity | Criteria |
|----------|----------|
| **High** | Assets can be stolen/lost/compromised directly, or protocol can be manipulated to cause significant harm |
| **Medium** | Assets not at direct risk, but function/availability of protocol could be impacted, or leak value with hypothetical attack path |
| **Low** | Low impact issues, unlikely edge cases, informational |
| **Gas** | Gas optimization suggestions |
| **QA** | Code quality, documentation, non-critical |

## Quality Assurance Report Section
```markdown
## QA Report

### [L-01] Missing zero address validation
**Instances:** 3
- Contract.sol#L50
- Contract.sol#L75
- Token.sol#L20

### [L-02] Use of deprecated functions
...

### [NC-01] Inconsistent naming convention
...

### [NC-02] Missing NatSpec documentation
...
```
