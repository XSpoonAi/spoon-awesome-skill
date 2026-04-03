# Single Finding Templates

## Minimal Format
```markdown
### [SEV-##] Title

**Severity:** High  
**Location:** `Contract.sol#L100`

**Issue:** [Description]

**Fix:** [Recommendation]
```

## Standard Format
```markdown
## [H-01] Title of Vulnerability

### Severity
High

### Location
- File: `src/Contract.sol`
- Lines: 100-120
- Function: `withdraw()`

### Description
[Detailed explanation of the vulnerability]

### Impact
[What can go wrong]

### Proof of Concept
```solidity
function test_exploit() public {
    // Attack code
}
```

### Recommendation
```solidity
// Fixed code
```
```

## Detailed Format (for Critical/High)
```markdown
## [C-01] Critical: [Title]

### Summary
One-line summary.

### Severity Justification
- **Impact:** High - [reason]
- **Likelihood:** High - [reason]
- **Overall:** Critical

### Root Cause Analysis
The vulnerability exists because:
1. [Root cause 1]
2. [Root cause 2]

### Vulnerable Code
```solidity
// src/Contract.sol:L100-120
function vulnerable() external {
    // Problematic code
}
```

### Attack Scenario
1. Attacker does X
2. This causes Y
3. Result: Z

### Proof of Concept
```solidity
// test/Exploit.t.sol
function test_critical_exploit() public {
    uint256 before = token.balanceOf(attacker);
    
    vm.prank(attacker);
    target.vulnerable();
    
    uint256 after = token.balanceOf(attacker);
    assertGt(after, before, "Exploit successful");
}
```

### Recommendation
```solidity
function fixed() external {
    // Fixed implementation
}
```

### References
- [Similar vulnerability in Protocol X](link)
- [CWE-XXX](link)
```

## Gas Optimization Format
```markdown
### [G-01] Use `unchecked` for safe arithmetic

**Gas Saved:** ~200 gas per call

**Before:**
```solidity
for (uint256 i = 0; i < length; i++) {
    // ...
}
```

**After:**
```solidity
for (uint256 i = 0; i < length;) {
    // ...
    unchecked { ++i; }
}
```

**Instances:** 5
- Contract.sol#L50
- Contract.sol#L75
- Token.sol#L100
```

## QA/Informational Format
```markdown
### [I-01] Missing NatSpec documentation

**Description:** Functions lack proper documentation.

**Instances:**
- `Contract.sol#L50` - `deposit()`
- `Contract.sol#L75` - `withdraw()`

**Recommendation:** Add NatSpec comments for all public/external functions.
```
