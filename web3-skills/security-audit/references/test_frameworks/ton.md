# TON Testing Frameworks

## Blueprint (Official)

### Commands
```bash
npx create-ton my-project       # Create new project
npx blueprint create            # Create contract in existing project
npx blueprint build             # Compile contracts
npx blueprint test              # Run tests
npx blueprint run               # Run scripts
```

### Test Template (TypeScript)
```typescript
import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { Cell, toNano } from '@ton/core';
import { Target } from '../wrappers/Target';
import '@ton/test-utils';

describe('Target', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let attacker: SandboxContract<TreasuryContract>;
    let target: SandboxContract<Target>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();
        
        deployer = await blockchain.treasury('deployer');
        attacker = await blockchain.treasury('attacker');
        
        target = blockchain.openContract(
            Target.createFromConfig({
                owner: deployer.address,
            }, code)
        );

        await target.sendDeploy(deployer.getSender(), toNano('0.05'));
    });

    it('should demonstrate exploit', async () => {
        const balanceBefore = await attacker.getBalance();
        
        const result = await target.sendVulnerableMessage(
            attacker.getSender(),
            toNano('1')
        );
        
        expect(result.transactions).toHaveTransaction({
            from: attacker.address,
            to: target.address,
            success: true,
        });
        
        const balanceAfter = await attacker.getBalance();
        expect(balanceAfter).toBeGreaterThan(balanceBefore);
    });
});
```

### Wrapper Template
```typescript
import { Address, beginCell, Cell, Contract, ContractProvider, Sender } from '@ton/core';

export class Target implements Contract {
    constructor(readonly address: Address, readonly init?: { code: Cell; data: Cell }) {}

    static createFromConfig(config: TargetConfig, code: Cell): Target {
        const data = beginCell()
            .storeAddress(config.owner)
            .storeUint(0, 64)
            .endCell();
        return new Target(contractAddress(0, { code, data }), { code, data });
    }

    async sendVulnerableMessage(provider: ContractProvider, via: Sender, value: bigint) {
        await provider.internal(via, {
            value,
            body: beginCell()
                .storeUint(0x12345678, 32)
                .endCell(),
        });
    }

    async getBalance(provider: ContractProvider) {
        const state = await provider.getState();
        return state.balance;
    }
}
```

## Tact Language Testing

### Tact Contract Example
```tact
import "@stdlib/deploy";

contract Target with Deployable {
    owner: Address;
    balance: Int;

    init(owner: Address) {
        self.owner = owner;
        self.balance = 0;
    }

    receive("withdraw") {
        // Vulnerable: missing owner check
        send(SendParameters{
            to: sender(),
            value: self.balance,
            mode: SendRemainingBalance
        });
    }

    get fun balance(): Int {
        return self.balance;
    }
}
```

### Tact Test Template
```typescript
import { Blockchain, SandboxContract } from '@ton/sandbox';
import { toNano } from '@ton/core';
import { Target } from '../build/Target/tact_Target';

describe('Tact Target', () => {
    let blockchain: Blockchain;
    let target: SandboxContract<Target>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();
        target = blockchain.openContract(await Target.fromInit(deployer.address));
    });

    it('exploit missing owner check', async () => {
        const attacker = await blockchain.treasury('attacker');
        
        // Deposit funds first
        await target.send(deployer.getSender(), { value: toNano('10') }, null);
        
        // Attacker withdraws without being owner
        const result = await target.send(
            attacker.getSender(),
            { value: toNano('0.05') },
            "withdraw"
        );
        
        expect(result.transactions).toHaveTransaction({
            success: true,
            from: target.address,
            to: attacker.address,
        });
    });
});
```

## @tact-lang/emulator

### Direct Emulator Usage
```typescript
import { ContractExecutor, ContractSystem } from '@tact-lang/emulator';

const system = await ContractSystem.create();
const treasure = await system.treasure('treasure');

const contract = system.open(await Target.fromInit(treasure.address));
await contract.send(treasure, { value: toNano('10') }, "deposit");

// Track all transactions
const tracker = system.track(contract.address);
await contract.send(attacker, { value: toNano('0.05') }, "withdraw");

expect(tracker.collect()).toHaveTransaction({
    success: true
});
```

## FunC Contract Testing

### FunC Test Pattern
```typescript
import { compile } from '@ton/blueprint';

describe('FunC Contract', () => {
    let code: Cell;

    beforeAll(async () => {
        code = await compile('Target');
    });

    it('should test FunC exploit', async () => {
        const blockchain = await Blockchain.create();
        
        const target = blockchain.openContract(
            Target.createFromCode(code, initialData)
        );
        
        // Test exploit
    });
});
```

## Useful Assertions
```typescript
expect(result.transactions).toHaveTransaction({
    from: sender.address,
    to: target.address,
    success: true,
    exitCode: 0,
    outMessagesCount: 1,
});

expect(result.transactions).not.toHaveTransaction({
    success: false,
});
```
