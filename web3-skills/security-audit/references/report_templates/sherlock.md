# Sherlock Report Template

## Report Structure
```markdown
# [Protocol Name] Security Review

**Auditor:** [Name]  
**Date:** [Date]  
**Commit:** [hash]
```

## Finding Template (Sherlock Style)
```markdown
## [Auditor Handle] - [Title]

### Summary
One-line summary of the issue.

### Root Cause
In [Contract.sol:L100](link), the [specific issue] occurs because [root cause explanation].

### Internal pre-conditions
1. [Condition 1 that must be true]
2. [Condition 2 that must be true]

### External pre-conditions
1. [External condition, e.g., "Token price drops by 50%"]
2. [Market condition or external dependency]

### Attack Path
1. Attacker calls `functionA()` with parameter X
2. This triggers [specific behavior]
3. Attacker then calls `functionB()`
4. Result: [outcome]

### Impact
[Quantified impact]
- Loss: Up to X% of TVL
- Affected parties: [who is harmed]

### PoC
```solidity
function test_exploit() public {
    // Setup
    vm.startPrank(attacker);
    
    // Attack
    target.vulnerableFunction();
    
    // Verify
    assertGt(attacker.balance, initialBalance);
}
```

### Mitigation
```solidity
// Add validation
require(amount <= maxAllowed, "Exceeds limit");
```
```

## Severity Criteria (Sherlock)

### High
- Definite loss of funds without limiting factors
- Direct theft, freezing of funds, protocol insolvency
- Permanent DoS of critical functionality

### Medium
- Conditional loss of funds (requires external conditions)
- Temporary DoS
- Griefing attacks with moderate impact
- Theft of yield/fees (not principal)

### Low/Informational
- Issues with no direct monetary impact
- Best practice violations
- Gas optimizations

## Sherlock-Specific Sections

### Escalation Section
```markdown
### Escalation

**Escalated by:** [Handle]

**Reason:** [Why this should be reconsidered]

**Additional context:** [New information]
```

### Duplicate Marking
```markdown
**Duplicates:**
- #12
- #34
- #56

**Selected as best:** This submission provides the clearest PoC and mitigation.
```

## Report Footer
```markdown
---
## Disclaimer

This audit report is not financial advice. The findings represent the auditor's assessment at the time of review. No guarantees are made about the security of the protocol.
```
