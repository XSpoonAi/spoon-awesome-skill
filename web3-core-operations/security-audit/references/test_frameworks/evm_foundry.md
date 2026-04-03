# Foundry (EVM)

## Commands
```bash
forge init                    # Initialize new project
forge build                   # Compile contracts
forge test                    # Run all tests
forge test -vvvv              # Verbose output with traces
forge test --match-test testX # Run specific test
forge test --fork-url <RPC>   # Fork mainnet
forge script Script.s.sol     # Run deployment script
cast call <addr> "func()"     # Read contract
cast send <addr> "func()"     # Write contract
anvil                         # Local testnet
```

## Test Template
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/Target.sol";

contract ExploitTest is Test {
    Target target;
    address attacker = makeAddr("attacker");
    address victim = makeAddr("victim");

    function setUp() public {
        target = new Target();
        vm.deal(attacker, 10 ether);
        vm.deal(victim, 10 ether);
    }

    function testExploit() public {
        vm.startPrank(attacker);
        
        // Attack logic here
        
        vm.stopPrank();
        
        // Assert exploit success
        assertGt(attacker.balance, 10 ether);
    }
}
```

## Fork Testing
```solidity
contract ForkTest is Test {
    uint256 mainnetFork;
    
    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"));
        vm.selectFork(mainnetFork);
    }
    
    function testForkExploit() public {
        vm.rollFork(18_000_000); // Specific block
        // Test against real state
    }
}
```

## Cheatcodes
```solidity
vm.prank(address)           // Next call from address
vm.startPrank(address)      // All calls from address
vm.stopPrank()              // Stop prank
vm.deal(address, amount)    // Set ETH balance
vm.warp(timestamp)          // Set block.timestamp
vm.roll(blockNumber)        // Set block.number
vm.expectRevert()           // Expect next call to revert
vm.expectEmit()             // Expect event emission
vm.mockCall()               // Mock external call
vm.label(address, "name")   // Label address in traces
```

## Flash Loan Test Pattern
```solidity
interface IFlashLender {
    function flashLoan(address, address, uint256, bytes calldata) external;
}

contract FlashLoanExploit is Test {
    function testFlashLoanAttack() public {
        IFlashLender lender = IFlashLender(AAVE_POOL);
        
        vm.startPrank(attacker);
        lender.flashLoan(
            address(this),
            WETH,
            1000 ether,
            abi.encode(attackData)
        );
        vm.stopPrank();
    }
    
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        // Attack logic during flash loan
        
        // Repay
        IERC20(asset).approve(msg.sender, amount + premium);
        return true;
    }
}
```
