# Hardhat (EVM)

## Commands
```bash
npx hardhat init                    # Initialize project
npx hardhat compile                 # Compile contracts
npx hardhat test                    # Run all tests
npx hardhat test test/X.ts          # Run specific test
npx hardhat node                    # Local testnet
npx hardhat run scripts/deploy.ts   # Run script
npx hardhat console                 # Interactive console
```

## Test Template (TypeScript)
```typescript
import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-network-helpers";

describe("ExploitTest", function () {
  async function deployFixture() {
    const [owner, attacker, victim] = await ethers.getSigners();
    
    const Target = await ethers.getContractFactory("Target");
    const target = await Target.deploy();
    
    return { target, owner, attacker, victim };
  }

  it("should demonstrate exploit", async function () {
    const { target, attacker, victim } = await loadFixture(deployFixture);
    
    const attackerBalanceBefore = await ethers.provider.getBalance(attacker.address);
    
    // Attack logic
    await target.connect(attacker).vulnerableFunction();
    
    const attackerBalanceAfter = await ethers.provider.getBalance(attacker.address);
    expect(attackerBalanceAfter).to.be.gt(attackerBalanceBefore);
  });
});
```

## Fork Testing
```typescript
import { ethers, network } from "hardhat";

describe("Fork Test", function () {
  before(async function () {
    await network.provider.request({
      method: "hardhat_reset",
      params: [{
        forking: {
          jsonRpcUrl: process.env.ETH_RPC_URL,
          blockNumber: 18000000
        }
      }]
    });
  });

  it("should test against mainnet state", async function () {
    const weth = await ethers.getContractAt("IERC20", WETH_ADDRESS);
    const balance = await weth.balanceOf(WHALE_ADDRESS);
    expect(balance).to.be.gt(0);
  });
});
```

## Network Helpers
```typescript
import { 
  time, 
  mine, 
  setBalance,
  impersonateAccount 
} from "@nomicfoundation/hardhat-network-helpers";

// Time manipulation
await time.increase(3600);              // Increase by 1 hour
await time.increaseTo(timestamp);       // Set to specific time
await time.latest();                    // Get current timestamp

// Block manipulation
await mine(100);                        // Mine 100 blocks

// Balance manipulation
await setBalance(address, parseEther("100"));

// Account impersonation
await impersonateAccount(whaleAddress);
const whale = await ethers.getSigner(whaleAddress);
```

## Flash Loan Test Pattern
```typescript
describe("Flash Loan Attack", function () {
  it("should execute flash loan attack", async function () {
    const { attacker, target } = await loadFixture(deployFixture);
    
    const Exploit = await ethers.getContractFactory("FlashLoanExploit");
    const exploit = await Exploit.connect(attacker).deploy(target.address);
    
    const balanceBefore = await ethers.provider.getBalance(attacker.address);
    
    await exploit.executeAttack();
    
    const balanceAfter = await ethers.provider.getBalance(attacker.address);
    expect(balanceAfter).to.be.gt(balanceBefore);
  });
});
```

## Config (hardhat.config.ts)
```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      forking: {
        url: process.env.ETH_RPC_URL || "",
        enabled: true
      }
    }
  }
};

export default config;
```
